import collections
import datetime
import json
import typing
import requests
import logging


from django import views
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from telebot import TeleBot
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank, SearchHeadline, SearchVectorField
from django.views.generic import ListView
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
    SearchRank,
    SearchHeadline)
from django.core import serializers
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core import serializers
from django.views.generic import ListView

from .forms import (
    ContractCreateForm,
    ContractInfoForm,
    ContractHistorySearchForm,
    LoginForm,
    ContractInfoFormInternet,
    ContractInfoFormTelevision,
)
from .models import (
    STATUS_CHOICE,
    CONDITIONS_CHOICE,
    Contract,
    STATE_NOTPROCESSED,
    STATE_REPROCESSING,
    STATUS_INCORRECT,
    STATE_COMPLETE,
    STATUS_WORKS,
    STATUS_COMPLETE,
    STATE_LATER,
    STATE_INPROGRESS,
    STATUS_NONE, CommentRow,
    FrontUser, Statistic, STATISTIC_NO_AUTO_ASSIGN, User
)

logger_info = logging.getLogger('sms_cry_information')
logger_error = logging.getLogger('sms_cry_errors')
logger_response = logging.getLogger('sms_cry_response')

bot_name = settings.TELEGRAM_BOT_NAME
bot = TeleBot(settings.TELEGRAM_BOT_API_KEY)

class LoginView(views.View):
    a = 23124
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form}
        return render(request, 'User/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/contract/')
        return render(request, 'User/login.html', {'form': form})

def permission(request):
    return render(request, 'User/permission.html')


def profile(request):
    return render(request, 'User/profile.html')

def dict2html(data, model):
    res = []
    for key, value in data.items():
        localized_key = model._meta.get_field(key).verbose_name
        choices = model._meta.get_field(key).choices
        data = value
        if choices:
            data = ""
            for k1, valid_display in choices:
                for k2 in value:
                    if k1 == k2:
                        data += f"<span class='db_span_field_{k1}'>{valid_display}</span>"
                        data += " "

        if isinstance(data, bool):
            data = "????" if data else "??????"

        res.append(
            f"<div class='db_field db_field_{key}'>"
            f"   <strong>{localized_key}:</strong> {data}"
            f"</div>")

    return "".join(res)

def dictDiff2html(data):
    res = []
    for key, diff in data.items():
        res.append(
            f"<div class='db_field db_field_{key}'>"
            f"   <strong>{diff['localized_key']}:</strong> "
            f"   {diff['old']} <strong>???????????????? ????</strong> {diff['new']}"
            f"</div>"
        )
    return "".join(res)

def filter_away_users(online, offline):
    res = []

    for on_item in online: 
        is_away = False 
        for off_item in offline:
            if on_item["username"] == off_item["username"]:
                is_away = True
                break

        if not is_away:
            res.append(on_item)
    return res

def get_users():
    url = 'http://dev.noc.shtorm.net/api/voip/register/sales/'
    token = "c1f45fba1b463abf5a92aaf339d6b6e9c93b013d"
    headers = {"Authorization": f"Token {token}", 'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


def get_active_users():
    data = get_users()

    online = list(filter(lambda item: int(item["status"]) == 1, data))
    offline = list(filter(lambda item: int(item["status"]) == 0, data))

    valid_users = filter_away_users(online, offline)
    f = map(lambda item: item["username"], valid_users)
    return list(f)


def least_workload_user(users):
    contracts = Contract.objects.filter(state__in=[STATE_NOTPROCESSED, STATE_INPROGRESS]).values("user")
    contract_users = list(map(lambda x: x["user"], contracts))
    for user in users:
        if user.id not in contract_users:
            return user


def least_active_user():
    active_users = get_active_users()
    found_users = FrontUser.objects \
        .filter(username__in=active_users) \
        .order_by("-done_count")

    if not found_users.exists():
        return

    user = least_workload_user(found_users)
    if user is None:
        return

    return FrontUser.objects.get(username=user)


@login_required(login_url='/login')
@permission_required('front.contract_create', login_url='/permission')
def contract_new(request):
    form = ContractCreateForm()


    if request.method == "POST":
        form = ContractCreateForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.state = STATE_NOTPROCESSED

            assign_user = least_active_user()
            if assign_user is not None:
                contract.user = assign_user
                contract.state = STATE_INPROGRESS
                contract.status = STATUS_WORKS
                userid = assign_user.id_telegram
                if not userid == 0:
                    bot.send_message(userid, '?????? ???????????? ????????????')
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"???????????????????????? {assign_user} ?????????????? ????????????")
            else:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"?????? ???????????????????????? ????????????, ???????????? ???????????????????? ?? ????????????????")
                Statistic.log(STATISTIC_NO_AUTO_ASSIGN)

            contract.save()

            create_text = f"?????????????? ???????????? ?? ??????????????????????: {dict2html(form.cleaned_data, contract)}"
            if assign_user is not None:
                create_text += "<br>"
                create_text += f"???????????????????????? {assign_user} ?????????????? ????????????"

            comment_text = request.POST.get("comment")
            comment_row = CommentRow(
                user=request.user,
                text=comment_text,
                changes=create_text)
            comment_row.save()

            contract.comments.add(comment_row)

            messages.add_message(
                request,
                messages.SUCCESS,
                f"?????????????? ?????????????? ?????? ?????????????? #{contract.id}")
            form = ContractCreateForm()  # reset form
            return redirect("contract_new")

    return render(request, "Contract/register_contract.html", {"form": form})

@permission_required('front.contract_take', login_url='/permission')
def contract_take(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    contract.user = request.user
    contract.state = STATE_INPROGRESS
    contract.status = STATUS_WORKS
    contract.save()

    contract.history_add(request.user, "?????????? ????????????")
    return redirect(reverse("contract_consider", args=[contract.id]))

def random_contract() -> typing.Optional[Contract]:
    """???????????? ?????????????????? ???????????? ?? ???????????? ????????????????????, ???????? ?????????? ???? ??????????, ???? ???????????? None"""
    priority = []
    for item in Contract.objects.filter(~Q(status=STATUS_COMPLETE), user__isnull=True):
        p = 0
        if item.state == STATE_NOTPROCESSED and item.status == STATUS_NONE:
            p = 1
        if item.from_office:
            p = 2

        priority.append([item, p])

    priority = sorted(priority, key=lambda i: i[1], reverse=True)
    if len(priority) == 0:
        return None

    contract = priority[0][0]
    return contract

def contract_take_random(request):
    contract = random_contract()
    if contract is None:
        messages.add_message(request, messages.WARNING, "?????? ???????????????????? ????????????")
        return redirect(reverse("contract_list"))

    contract.user = request.user
    contract.state = STATE_INPROGRESS
    contract.status = STATUS_WORKS
    contract.save()

    contract.history_add(request.user, "?????????? ???????????? ????????????????")
    return redirect(reverse("contract_consider", args=[contract.id]))


def clean_none(data):
    exclude = [None, 0, "0", ""]
    return {k: v for (k, v) in data.items() if v not in exclude}


def history_search_form(data=None):
    form = ContractHistorySearchForm(data=data)
    users = FrontUser.objects.all()
    form.fields["created_by"].choices = [(None, "???? ??????????????"), ] + [
        (user.id, user.username) for user in users]
    return form


@login_required(login_url='/login')
def contract_archive(request):
    search_form = history_search_form(request.GET)
    filter_args = {}
    if search_form.is_valid():
        filter_args = clean_none(search_form.cleaned_data)

    if filter_args.get("user"):
        filter_args["user"] = int(filter_args["user"])

    filter_args.update({"state": STATE_COMPLETE})
    contracts = Contract.objects.filter(**filter_args).order_by("-id")
    return render(
        request, "Contract/history_contract.html", {
            "contracts":   contracts,
            "search_form": search_form
        })


class SearchRankCD(SearchRank):
    function = 'ts_rank_cd'

    def __init__(self, vector, query, normalization = 0, **extra):
        super(SearchRank, self).__init__(
            vector, query, normalization, **extra)

class ContractArchiveSearch(ListView):
    template_name = 'Contract/history_contract.html'

    def get_context_data(self, **kwargs):
        include = [STATE_COMPLETE]
        context = super(ContractArchiveSearch, self).get_context_data()
        text = self.request.GET.get("text")

        vector = SearchVector('name', 'city', 'phone', 'address')
        query = SearchQuery(' & '.join([term + ':*' for term in text.split(' ') if len(term)]),
                            search_type = 'raw', config = 'russian')
        search_headline = SearchHeadline('name', query)


        contracts = Contract.objects \
            .annotate(rank = SearchRank(vector, query)) \
            .annotate(headline = search_headline) \
            .filter(rank__gte = 0.001) \
            .filter(state__in=include) \
            .order_by("-rank")

        context['vector'] = vector
        context['contracts'] = contracts
        context['text'] = text
        return context

    def get_queryset(self):
        text = self.request.GET.get("text")
        query = SearchQuery(
            ' & '.join([term + ':*' for term in text.split(' ') if len(term)]),
            search_type='raw', config='russian')
        return Contract.objects.all() \
            .filter(tsv=query) \
            .annotate(rank=SearchRankCD(models.F('tsv'), query))


class ContractSearch(ListView):
    template_name = 'list_contract.html'

    def get_context_data(self, **kwargs):
        include = [STATE_NOTPROCESSED, STATE_INPROGRESS, STATE_REPROCESSING]
        context = super(ContractSearch, self).get_context_data()
        text = self.request.GET.get("text")

        vector = SearchVector('name', 'city', 'phone', 'address')
        query = SearchQuery(' & '.join([term + ':*' for term in text.split(' ') if len(term)]),
                            search_type = 'raw', config = 'russian')
        search_headline = SearchHeadline('name', query)


        contracts = Contract.objects \
            .annotate(rank = SearchRank(vector, query)) \
            .annotate(headline = search_headline) \
            .filter(rank__gte = 0.001) \
            .filter(state__in=include) \
            .order_by("-rank")

        context['vector'] = vector
        context['contracts'] = contracts
        context['text'] = text
        return context

    def get_queryset(self):
        text = self.request.GET.get("text")
        query = SearchQuery(
            ' & '.join([term + ':*' for term in text.split(' ') if len(term)]),
            search_type='raw', config='russian')
        return Contract.objects.all() \
            .filter(tsv=query) \
            .annotate(rank=SearchRankCD(models.F('tsv'), query))

#@permission_required('front.contract_browse_statistics', login_url='/permission')
def collect_contract_statistic():
    res = collections.defaultdict(int)
    for item in Contract.objects.all().values("user", "state"):
        key = item["state"]
        if item["user"] is not None:
            res["assigned"] += 1
            continue
        res[key] += 1

    return {
        "contract_waiting":          res[STATE_NOTPROCESSED],
        "contract_pending":          res[STATE_INPROGRESS],
        "contract_waiting_assigned": res["assigned"]
    }


@permission_required('front.contract_browse', login_url='/permission')
def contract_list(request):
    include = [STATE_NOTPROCESSED, STATE_REPROCESSING]
    contracts = Contract.objects.filter(state__in=include, user__isnull=True).order_by(
        "-id")
    return render(
        request,
        "Contract/list_contract.html",
        {"contracts": contracts, **collect_contract_statistic()})


def contract_list_my(request):
    #include = [STATE_NOTPROCESSED, STATE_REPROCESSING, STATE_INPROGRESS]
    contracts = Contract.objects.filter(user=request.user).order_by("-id")
    contractcs = Contract.objects.filter(created_by=request.user, create_date__gte=timezone.now() - datetime.timedelta(hours=24)).order_by("-id")

    if request.method == "POST":
        comment = request.POST.get("comment")
        contract_id = request.POST.get("contracts")
        contract = get_object_or_404(Contract, pk=contract_id)
        contract.comment_add(request.user, comment)
        return redirect(contract_list_my)


    return render(
        request,
        "Contract/contract_list_my.html",
        {
            "contracts":  contracts, **collect_contract_statistic(),
            "contractcs": contractcs,
        }
    )


def contract_list_by_status(request, status=None):
    contracts = Contract.objects.filter(state__in=[status]).order_by("-id")
    return render(
        request,
        "Contract/list_contract.html",
        {"contracts": contracts, **collect_contract_statistic()})

@login_required(login_url='/login')
def contract_list_later(request):
    include = [STATE_LATER]
    contracts = Contract.objects.filter(state__in=include, user=request.user).order_by(
        "-id")
    return render(
        request,
        "Contract/list_contract.html",
        {"contracts": contracts, **collect_contract_statistic()})

@login_required(login_url='/login')
def contract_list_active(request):
    include = [STATE_INPROGRESS, STATE_REPROCESSING]
    contracts = Contract.objects.filter(state__in=include, user__isnull=False).order_by(
        "-id")
    return render(
        request,
        "Contract/list_contract.html",
        {"contracts": contracts})


# @login_required(login_url='/login')
# def contract_list_delayed(request):
#     contracts = Contract.objects.filter(plain_later__isnull=False).order_by("-id")
#     return render(
#         request,
#         "Contract/list_contract.html",
#         {"contracts": contracts, **collect_contract_statistic()})


def localized_key(model, key):
    return model._meta.get_field(key).verbose_name


def diff_with_post(data, contract):
    res = {}
    for changed_key in data:
        field_key = changed_key

        if field_key == "csrfmiddlewaretoken":
            continue

        localized = localized_key(contract, field_key)
        old = getattr(contract, changed_key)
        new = data[changed_key]

        res.update(
            {
                field_key: {
                    "localized_key": localized,
                    "old":           old,
                    "new":           new
                }
            })

    return res

def diff_with_form(form, contract):
    res = {}
    for changed_key in form.changed_data:
        field_key = changed_key

        localized = localized_key(contract, field_key)
        old = getattr(contract, changed_key)
        new = form.cleaned_data[changed_key]

        if hasattr(contract, f"get_{field_key}_display"):
            old = getattr(contract, f"get_{field_key}_display")()
            new = dict(form.fields.get(field_key).choices).get(form.cleaned_data.get(field_key))
            #new = dict(form.fields[field_key].choices)[form.cleaned_data[field_key]]

        res.update(
            {
                field_key: {
                    "localized_key": localized,
                    "old":           old,
                    "new":           new
                }
            })

    return res


@login_required(login_url='/login')
@permission_required('front.contract_browse', login_url='/permission')
def contract_consider(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    info_form = ContractInfoForm(instance=contract)
    info_form_in = ContractInfoFormInternet(instance=contract)
    info_form_tv = ContractInfoFormTelevision(instance=contract)
    
    myusername = str(request.user)
    myphone = contract.phone
    address = contract.address
    name = 'name'
    contracts = Contract.objects.all()
    for contract in contracts:
        data = [
            contract.name, contract.phone, contract.city, contract.status
        ]
        data = map(str, data)
        # logger_info.info(' | '.join(data))
        logger_error.error('jkxahdaisdhfhasdfhjasdf')
        # logger_response.debug('debug messege')

    if request.method == "POST":
        comment = request.POST.get("comment")
        contract.comment_add(request.user, comment)
        return redirect(contract_consider, contract_id)

    return render(
        request, "Contract/consider_contract.html", {
            "contract_id": contract_id,
            "info_form":   info_form,
            "info_form_in": info_form_in,
            "info_form_tv": info_form_tv,
            "contract":    contract,
            "users":       FrontUser.objects.all()
        })


@login_required(login_url='/login')
def contract_update(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    info_form = ContractInfoForm(instance=contract)

    if request.method == "POST":
        form = ContractInfoForm(data=request.POST, instance=contract)
        if form.is_valid():
            diff = diff_with_form(
                form,
                Contract.objects.get(pk=contract_id))
            contract.save()
            cmnt = CommentRow(user=request.user, changes=dictDiff2html(diff))
            cmnt.save()

            contract.comments.add(cmnt)
        return redirect(contract_consider, contract_id)

    return render(request, "Contract/consider_contract.html", {
        "contract_id": contract_id,
        "info_form": info_form,
        "contract": contract,
        "users": User.objects.all()
    })

def contract_update_internet(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    info_form_in = ContractInfoFormInternet(instance=contract)

    if request.method == "POST":
        form = ContractInfoFormInternet(data=request.POST, instance=contract)
        if form.is_valid():
            diff = diff_with_form(
                form,
                Contract.objects.get(pk=contract_id))
            contract.save()
            cmnt = CommentRow(user=request.user, changes=dictDiff2html(diff))
            cmnt.save()

            contract.comments.add(cmnt)
        return redirect(contract_consider, contract_id)

    return render(request, "Contract/consider_contract.html", {
        "contract_id": contract_id,
        "info_form_in": info_form_in,
        "contract": contract,
        "users": User.objects.all()
    })

def contract_update_television(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    info_form_tv = ContractInfoFormTelevision(instance=contract)

    if request.method == "POST":
        form = ContractInfoFormTelevision(data=request.POST, instance=contract)
        if form.is_valid():
            diff = diff_with_form(
                form,
                Contract.objects.get(pk=contract_id))
            contract.save()
            cmnt = CommentRow(user=request.user, changes=dictDiff2html(diff))
            cmnt.save()

            contract.comments.add(cmnt)
        return redirect(contract_consider, contract_id)

    return render(request, "Contract/consider_contract.html", {
        "contract_id": contract_id,
        "info_form_in": info_form_tv,
        "contract": contract,
        "users": User.objects.all()
    })

def contract_call(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    if contract.call_date is not None:
        messages.add_message(request, messages.ERROR, "???? ???????? ???????????? ?????? ?????? ????????????")
        return redirect(reverse("Contract/contract_list"))

    contract.call_date = datetime.datetime.now()
    contract.save()

    messages.add_message(request, messages.SUCCESS, "??????????????")
    return redirect(reverse("Contract/contract_detail", args=[contract_id]))

@login_required(login_url='/login')
def contract_return(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)

    if contract.status == STATUS_COMPLETE or contract.status == STATUS_INCORRECT:
        contract.state = STATE_COMPLETE
        contract.user = None
        messages.add_message(request, messages.SUCCESS, "?????????????? ??????????????")

    if contract.state == STATE_INPROGRESS:
        contract.state = STATE_NOTPROCESSED
        contract.status = STATUS_NONE
        contract.user = None
        contract.history_add(request.user, "???????????? ???????????? ?? ???????????????? ??????????????????")
        messages.add_message(
            request,
            messages.SUCCESS,
            "???????????? ???????? ????????????????????, ?????????????????? ?????????????????? ???????? ????????????.")

    contract.save()

    # ???????????? ?????????????????? ???????????? ???????? ?????????? ???????? ?????????? ???????????? None
    if not Contract.objects.filter(user=request.user).exists():
        new_contract = random_contract()
        if new_contract is None:
            messages.add_message(
                request,
                messages.WARNING,
                "?????? ???????????????????? ???????????? ?????? ???????? ????????????????????")
            return redirect(reverse("Contract/contract_list"))
        else:
            new_contract.user = request.user
            new_contract.state = STATE_INPROGRESS
            new_contract.status = STATUS_WORKS
            new_contract.save()
            new_contract.history_add(request.user, "?????????? ???????????? ????????????????")
            messages.add_message(
                request,
                messages.WARNING,
                "?????? ???????????? ?????????? ????????????")
            return redirect(reverse("Contract/contract_return"))

    # assign_user= least_active_user()
    # if assign_user is not None:
    #     contract.user = assign_user
    #     contract.state = STATE_INPROGRESS
    # else:
    #     Statistic.log(STATISTIC_NO_AUTO_ASSIGN)

    return redirect(reverse("Contract/contract_return", args=[contract.id]))

def contract_not_contact(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)

    if request.method == "POST":
        comment = request.POST.get("comment")
        contract.comment_add(request.user, comment)
        messages.add_message(
            request,
            messages.WARNING,
            "???? ?????????????? ???????????? ?? '???????????????? ??????????????????'")
        return redirect(contract_list)

    return render(request, "Contract/contract_not_contact.html", {
        "contract_id": contract_id,
        "contract": contract,
        "users": FrontUser.objects.all()
    })


@login_required(login_url='/login')
def contract_plain_later(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    new_date = request.POST.get("planning_later")
    is_infinity = bool(request.POST.get("infinity_delay"))
    if not new_date and not is_infinity:
        messages.add_message(request, messages.ERROR, "???? ???? ?????????????? ?????????? ????????")
        return redirect("/contract")

    if contract.plain_later:
        messages.add_message(request, messages.ERROR, "???????? ?? ???????? ???????????? ?????? ??????????????")
        return redirect("/contract")

    changes = "???????????????? ???????????? ???? ?????????????????????????????? ????????"
    if not is_infinity:
        contract.plain_later = datetime.datetime.strptime(new_date, "%Y-%m-%dT%H:%M")
        changes = f"???????????????? ???????????? ???? {contract.plain_later}"
    else:
        contract.infinity_plain = True

    contract.save()
    contract.history_add(user=request.user, changes=changes)

    messages.add_message(request, messages.SUCCESS, "?????????????? ??????????????????????????")
    return redirect(reverse("Contract/contract_list_my"))


@login_required(login_url='/login')
@permission_required('front.contract_close')
def contract_plain_cancel(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    contract.plain_later = None
    contract.infinity_plain = False
    contract.state = STATE_NOTPROCESSED
    contract.save()
    contract.history_add(request.user, "???????????? ????????????????????")

    messages.add_message(request, messages.SUCCESS, "?????????????? ????????????????")
    return redirect(reverse("Contract/contract_consider", args=[contract.id]))


@login_required(login_url='/login')
@permission_required('front.contract_assign')
def contract_assign(request, contract_id):
    user_id = int(request.POST.get("new_user"))

    contract = get_object_or_404(Contract, pk=contract_id)
    user = get_object_or_404(FrontUser, pk=user_id)

    if contract.user == user:
        messages.add_message(
            request, messages.WARNING,
            "???????????? ????????????????????????, ?????????????? ?????? ???????????????? ?????????????????????? ???? ???????? ????????????????")
        return redirect(reverse("Contract/contract_consider", args=[contract.id]))

    contract.state = STATE_INPROGRESS
    contract.status = STATUS_WORKS
    contract.user = user
    contract.save()
    contract.history_add(
        request.user,
        f"???????????? ???????????? ?? ????????????: {user.first_name} {user.last_name}")

    messages.add_message(request, messages.SUCCESS, "???????????????????????? ????????????????")
    return redirect(reverse("Contract/contract_consider", args=[contract.id]))


@login_required(login_url='/login')
def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    info_form = ContractInfoForm(instance=contract)

    if request.method == "POST":
        review_form = ContractInfoForm(instance=contract, data=request.POST)
        if review_form.is_valid():
            data = review_form.save()
            info_form = ContractInfoForm(instance=data)
            messages.add_message(request, messages.SUCCESS, "?????????????? ??????????????")

    return render(
        request, "Contract/detail_contract.html", {
            "info_form": info_form,
            "contract":  contract,
            "status":    STATUS_CHOICE,
            "service":   CONDITIONS_CHOICE,
        })


@login_required(login_url='/login')
def contract_statistic(request):
    avg_call = 0
    contracts = Contract.objects.all()
    for x in contracts:
        if not x.call_date:
            continue
        diff = x.call_date - x.create_date
        avg_call += diff.seconds
    avg_call /= len(contracts)

    uavg = collections.defaultdict(list)
    for x in contracts:
        if not x.call_date:
            continue
        diff = x.call_date - x.create_date
        uavg[x.user].append(diff.seconds)

    avg_call_by_user = {}
    for user in uavg:
        res = 0
        for metric in uavg[user]:
            res += metric
        res /= len(uavg[user])
        avg_call_by_user[user] = res

    no_assign_sum = Statistic.objects.filter(name=STATISTIC_NO_AUTO_ASSIGN).count()
    return render(
        request, "Contract/statistic.html", {
            "avg_call":         avg_call,
            "avg_call_by_user": avg_call_by_user,
            "no_assign_sum":    no_assign_sum
        })


@login_required(login_url='/login')
@require_POST
def contract_bulk_status_preview(request):
    contract_ids = request.POST.getlist("contracts[]")
    if not contract_ids:
        messages.add_message(request, messages.ERROR, "???? ???? ?????????????? ???? ?????????? ????????????")
        return redirect(reverse("contract_list"))

    contract_ids = list(map(int, contract_ids))
    contracts = Contract.objects.filter(id__in=contract_ids)
    return render(
        request, "bulk_status_preview.html", {
            "contracts":        contracts,
            "status_available": STATUS_CHOICE,
            "contract_ids":     contract_ids
        })


@login_required(login_url='/login')
@require_POST
def contract_bulk_status_apply(request):
    contract_ids = request.POST.get("contract_ids")
    new_status = request.POST.get("new_status")
    if not contract_ids:
        return HttpResponse(content="Invalid status", status=400)

    if not new_status:
        messages.add_message(request, messages.ERROR, "???? ???? ?????????????? ????????????")
        return redirect(reverse("Contract/contract_list"))

    ids = json.loads(contract_ids)
    contracts = Contract.objects.filter(id__in=ids)
    for contract in contracts:
        contract.status = int(new_status)
        contract.save()
        contract.history_add(
            request.user,
            f"???????????????????? ?????????? ???????????? {contract.get_status_display()}")

    messages.add_message(request, messages.SUCCESS, "???? ?????????????? ???????????????? ????????????")
    return redirect(reverse("Contract/contract_list"))


@login_required(login_url='/login')
def contract_bulk_later_preview(request):
    contract_ids = request.POST.getlist("contracts[]")
    if not contract_ids:
        messages.add_message(request, messages.ERROR, "???? ???? ?????????????? ???? ?????????? ????????????")
        return redirect(reverse("Contract/contract_list"))

    contract_ids = list(map(int, contract_ids))
    contracts = Contract.objects.filter(id__in=contract_ids)
    return render(
        request, "bulk_later_preview.html", {
            "contracts":    contracts,
            "contract_ids": contract_ids
        })


@login_required(login_url='/login')
@require_POST
def contract_bulk_later_apply(request):
    contract_ids = request.POST.get("contract_ids")
    new_date = request.POST.get("new_date")
    is_infinity = request.POST.get("is_infinity")
    if not contract_ids:
        return HttpResponse(content="???? ???????????????? ??????????????????", status=400)

    if not new_date and not is_infinity:
        messages.add_message(request, messages.ERROR, "???? ???? ?????????????? ?????????? ????????")
        return redirect(reverse("Contract/contract_list"))

    ids = json.loads(contract_ids)
    contracts = Contract.objects.filter(id__in=ids)
    for contract in contracts:
        if is_infinity:
            contract.plain_later = None
            contract.infinity_plain = True
            contract.state = STATE_LATER
            contract.history_add(request.user, f"???????????? ???????????????? ??????????????????")
            contract.save()
        else:
            contract.plain_later = datetime.datetime.strptime(new_date, "%Y-%m-%dT%H:%M")
            if contract.plain_later > datetime.datetime.now():
                contract.infinity_plain = False
                contract.state = STATE_LATER
                contract.history_add(
                    request.user,
                    f"???????????? ???????????????? ???? {contract.plain_later}")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "?????????????????? ???????? ???????????? ??????????????")
                return redirect(reverse("Contract/contract_consider", args=[contract.id]))
            contract.save()

        messages.add_message(
            request,
            messages.SUCCESS,
            "???? ?????????????? ???????????????????? ?????????? ????????")
        return redirect(reverse("Contract/contract_consider", args=[contract.id]))


def check_address(request):
    text = request.GET["text"]

    contracts = Contract.objects \
        .annotate(search=SearchVector('address')) \
        .filter(search=text)

    found = contracts.exists()


    data = serializers.serialize('python', contracts)

    return JsonResponse({"found": found, "data": data})
