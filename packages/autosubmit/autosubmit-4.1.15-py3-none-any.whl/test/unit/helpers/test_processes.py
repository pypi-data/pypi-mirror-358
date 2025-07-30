# Copyright 2015-2025 Earth Sciences Department, BSC-CNS
#
# This file is part of Autosubmit.
#
# Autosubmit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Autosubmit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Autosubmit.  If not, see <http://www.gnu.org/licenses/>.

from getpass import getuser
from psutil import ZombieProcess
from typing import List, Optional

import pytest

from autosubmit.helpers.processes import process_id, retrieve_expids


def _create_process(mocker, expid, username: Optional[str] = None, command='run', pid=1984):
    process = mocker.Mock()
    process.username.return_value = username or getuser()
    process.pid = pid
    process.cmdline.return_value = [
        'ENV=dev',
        'autosubmit',
        '-lc',
        'DEBUG',
        command,
        '--notransitive',
        expid,
        '-v'
    ]
    return process


@pytest.mark.parametrize(
    'expids,expected_retrieved,username',
    [
        [[], 0, None],
        [['a000'], 1, None],
        [['a000'], 0, '-droids you look'],
        [['a000', 'a001'], 2, None],
        [['a000', 'a001', 'error-not-an-expid!'], 2, None],
        [['error-not-an-expid!', 'hello-world'], 0, None]
    ],
    ids=[
        'No expids, none is retrieved',
        'One expid, one is retrieved',
        'One expid, but different (and invalid POSIX) user, none is retrieved',
        'Two expids, two are retrieved',
        'Three expids, but one expid is invalid, so only two are retrieved',
        'Two expids, none are valid, so none is retrievd',
    ]
)
def test_retrieve_expids(mocker, expids: List[str], expected_retrieved: int, username: Optional[str]):
    """Test the retrieval of experiment IDs.

    Test that given we are given N expids, and mock our way to have N processes
    for each experiment."""
    processes = [
        _create_process(mocker, expid, username) for expid in expids
    ]
    mocker.patch('autosubmit.helpers.processes.process_iter', return_value=processes)
    found = retrieve_expids()
    assert len(found) == expected_retrieved


def test_retrieve_expids_but_there_are_zombies_during_listing(mocker):
    """Test that when we see a ``ZombieProcess`` error during the listing the function returns as expected."""
    mocked_process = mocker.MagicMock()
    mocked_process.username.side_effect = ZombieProcess(0)
    mocker.patch('autosubmit.helpers.processes.process_iter', return_value=[mocked_process])
    expids = retrieve_expids()
    assert type(expids) is list and len(expids) == 0


def test_retrieve_expids_but_cmdline_raises_zombies(mocker):
    a000 = _create_process(mocker, 'a000', getuser())
    a001 = _create_process(mocker, 'a001', getuser())
    a001.cmdline.side_effect = ZombieProcess(1984)
    processes = [
        a000,
        a001
    ]
    mocker.patch('autosubmit.helpers.processes.process_iter', return_value=processes)
    expids = retrieve_expids()
    assert len(expids) == 1
    assert expids[0] in a000.cmdline()


@pytest.mark.parametrize(
    'expid,command,pid',
    [
        ['a000', 'run', 100],
        ['a000', 'create', 123]
    ]
)
def test_process_id(mocker, expid: str, command: str, pid: int):
    """Test the listing and identification Autosubmit processes."""
    processes = [_create_process(mocker, expid, command=command, pid=pid)]
    mocker.patch('autosubmit.helpers.processes.process_iter', return_value=processes)

    pid_found = process_id(expid, command)

    assert pid_found == pid


def test_process_id_nothing_found(mocker):
    """Test the listing and identification Autosubmit processes."""
    mocker.patch('autosubmit.helpers.processes.process_iter', return_value=[])

    pid_found = process_id('a000')

    assert pid_found is None


def test_process_id_multiple_found(mocker):
    """Test the listing and identification Autosubmit processes."""
    processes = [
        _create_process(mocker, 'a000', pid=1),
        _create_process(mocker, 'a000', pid=2)
    ]
    mocker.patch('autosubmit.helpers.processes.process_iter', return_value=processes)
    mocked_log = mocker.patch('autosubmit.helpers.processes.Log')

    pid_found = process_id('a000')

    assert pid_found is 1
    assert mocked_log.warning.call_count == 1


def test_process_id_but_there_are_zombies(mocker):
    """Test that if the listing of process crashes due to zombies, we get an empty list."""
    mocked_process = mocker.MagicMock()
    mocked_process.username.side_effect = ZombieProcess(0)
    mocker.patch('autosubmit.helpers.processes.process_iter', return_value=mocked_process)

    pid_found = process_id('a000')

    assert pid_found is None
