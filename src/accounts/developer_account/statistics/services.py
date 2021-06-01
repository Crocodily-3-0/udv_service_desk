from typing import List

from src.accounts.client_account.services import get_clients_db
from src.accounts.developer_account.statistics.schemas import AppealsStatistics, ClientsStatistics, \
    DevelopersStatistics, DeveloperStatistics, SoftwareStatistics, ModuleStatistics, StatusStatistics, ClientStatistics
from src.desk.services import get_appeals_by_developer, get_appeals_by_client, \
    get_appeals_by_software, get_appeals_by_module, get_appeals_db, get_status_distribution, get_statuses_list
from src.reference_book.services import get_software_db_list, get_modules
from src.users.logic import get_developers_db


async def get_software_list_stat() -> List[SoftwareStatistics]:
    softwares = await get_software_db_list()
    software_list = []
    for software in softwares:
        appeals = await get_appeals_by_software(software.id)
        count_appeals = len(appeals)
        software_list.append(SoftwareStatistics(name=software.name, count_appeals=count_appeals))
    return software_list


async def get_module_list_stat() -> List[ModuleStatistics]:
    modules = await get_modules()
    modules_list = []
    for module in modules:
        appeals = await get_appeals_by_module(module.id)
        count_appeals = len(appeals)
        modules_list.append(ModuleStatistics(name=module.name, count_appeals=count_appeals))
    return modules_list


async def get_status_list_stat() -> List[StatusStatistics]:
    appeals = await get_appeals_db()
    return await get_statuses_list(appeals)


async def get_appeals_statistics() -> AppealsStatistics:
    software_list = await get_software_list_stat()
    modules_list = await get_module_list_stat()
    statuses_list = await get_status_list_stat()
    await quick_sort(software_list)
    await quick_sort(modules_list)
    await quick_sort(statuses_list)
    software_list = software_list[::-1]
    modules_list = modules_list[::-1]
    statuses_list = statuses_list[::-1]
    return AppealsStatistics(software_list=software_list,
                             modules_list=modules_list,
                             statuses_list=statuses_list)


async def get_clients_statistics() -> ClientsStatistics:
    clients = await get_clients_db()
    clients_list = []
    for client in clients:
        appeals = await get_appeals_by_client(client.id)
        statuses = await get_status_distribution(appeals)
        count_appeals = len(appeals)
        open_statuses = statuses.registered + statuses.in_work + statuses.reopen
        closed = statuses.closed
        canceled = statuses.canceled
        clients_list.append(ClientStatistics(
            name=client.name,
            count_appeals=count_appeals,
            open_statuses=open_statuses,
            closed=closed,
            canceled=canceled
        ))
    await quick_sort(clients_list)
    clients_list = clients_list[::-1]
    return ClientsStatistics(clients_list=clients_list)


async def get_developers_statistics() -> DevelopersStatistics:
    developers = await get_developers_db()
    developers_list = []
    for developer in developers:
        appeals = await get_appeals_by_developer(str(developer.id))
        statuses = await get_status_distribution(appeals)
        count_appeals = len(appeals)
        open_statuses = statuses.registered + statuses.in_work + statuses.reopen
        closed_statuses = statuses.canceled + statuses.closed
        developers_list.append(DeveloperStatistics(
            name=developer.name,
            count_appeals=count_appeals,
            open_statuses=open_statuses,
            closed_statuses=closed_statuses
        ))
    await quick_sort(developers_list)
    developers_list = developers_list[::-1]
    return DevelopersStatistics(developers_list=developers_list)


async def partition(nums, low, high):
    # Выбираем средний элемент в качестве опорного
    # Также возможен выбор первого, последнего
    # или произвольного элементов в качестве опорного
    pivot = nums[(low + high) // 2].count_appeals
    i = low - 1
    j = high + 1
    while True:
        i += 1
        while nums[i].count_appeals < pivot:
            i += 1

        j -= 1
        while nums[j].count_appeals > pivot:
            j -= 1

        if i >= j:
            return j

        # Если элемент с индексом i (слева от опорного) больше, чем
        # элемент с индексом j (справа от опорного), меняем их местами
        nums[i], nums[j] = nums[j], nums[i]


async def quick_sort(nums):
    # Создадим вспомогательную функцию, которая вызывается рекурсивно
    async def _quick_sort(items, low, high):
        if low < high:
            # This is the index after the pivot, where our lists are split
            split_index = await partition(items, low, high)
            await _quick_sort(items, low, split_index)
            await _quick_sort(items, split_index + 1, high)

    await _quick_sort(nums, 0, len(nums) - 1)
