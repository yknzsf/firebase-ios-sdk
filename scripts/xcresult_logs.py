#!/usr/bin/env python

# Copyright 2019 Google
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prints logs from test runs captured in Apple .xcresult bundles
"""

import json
import os
import subprocess
import sys


def main():
  switches, args = parse_args(sys.argv[1:])
  if 'test' not in args:
    return

  xcresult_path = switches.get('-resultBundlePath')
  if xcresult_path is None:
    project = project_from_workspace_path(switches['-workspace'])
    scheme = switches['-scheme']
    xcresult_path = find_xcresult_path(project, scheme)

  log_id = find_log_id(xcresult_path)
  log = export_log(xcresult_path, log_id)
  sys.stdout.write(log)


def parse_args(args):
  """Parses switches from xcodebuild flags.
  """
  result = {}
  key = None
  rest = []
  for arg in args:
    if arg.startswith('-'):
      key = arg
    elif key is not None:
      result[key] = arg
      key = None
    else:
      rest.append(arg)

  return result, rest


def project_from_workspace_path(path):
  """Extracts the project name from a workspace path.
  Args:
    path: The path to a .xcworkspace file

  Returns:
    The project name from the basename of the path. For example, if path were
    'Firestore/Example/Firestore.xcworkspace', returns 'Firestore'.
  """
  root, ext = os.path.splitext(os.path.basename(path))
  if ext == '.xcworkspace':
    return root

  raise ValueError('%s is not a valid workspace path' % path)


def find_xcresult_path(project, scheme):
  """Finds an xcresult bundle for the given project and scheme.

  Args:
    project: The project name, like 'Firestore'
    scheme: The Xcode scheme that was tested

  Returns:
    The path to the newest xcresult bundle that matches.
  """
  project_path = find_project_path(project)
  bundle_dir = os.path.join(project_path, 'Logs/Test')
  prefix = 'Run-' + scheme + '-'

  xcresult = find_newest_matching_prefix(bundle_dir, prefix)
  if xcresult is None:
    raise LookupError(
        'Could not find xcresult bundle for %s in %s' % (scheme, bundle_dir))

  return xcresult


def find_project_path(project):
  """Finds the newest project output within Xcode's DerivedData.

  Args:
    project: A project name; the Foo in Foo.xcworkspace

  Returns:
    The path containing the newest project output.
  """
  path = os.path.expanduser('~/Library/Developer/Xcode/DerivedData')
  prefix = project + '-'

  # DerivedData has directories like Firestore-csljdukzqbozahdjizcvrfiufrkb. Use
  # the most recent one if there are more than one such directory matching the
  # project name.
  result = find_newest_matching_prefix(path, prefix)
  if result is None:
    raise LookupError(
        'Could not find project data for %s in %s' % (project, path))

  return result


def find_newest_matching_prefix(path, prefix):
  """Lists the given directory and returns the newest entry matching prefix.

  Args:
    path: A directory to list
    prefix: The starting part of any filename to consider

  Returns:
    The path to the newest entry in the directory whose basename starts with
    the prefix.
  """
  entries = os.listdir(path)
  result = None
  for entry in entries:
    if entry.startswith(prefix):
      fq_entry = os.path.join(path, entry)
      if result is None:
        result = fq_entry
      else:
        result_mtime = os.path.getmtime(result)
        entry_mtime = os.path.getmtime(fq_entry)
        if entry_mtime > result_mtime:
          result = fq_entry

  return result


def find_log_id(xcresult_path):
  """Finds the id of the test logs.

  Args:
    xcresult_path: The path to an xcresult bundle.

  Returns:
    The id of the test log output, suitable for use with xcresulttool get --id.
  """
  parsed = xcresulttool_json('get', '--path', xcresult_path)
  for action in parsed['actions']['_values']:
    if action['schemeCommandName']['_value'] != u'Test':
      continue

    return action['actionResult']['logRef']['id']['_value']

  raise ValueError('Could not find a log id in xcresult at %s' % xcresult_path)


def export_log(xcresult_path, log_id):
  """Exports the log data with the given id from the xcresult bundle.

  Args:
    xcresult_path: The path to an xcresult bundle.
    log_id: The id that names the log output (obtained by find_log_id)

  Returns:
    The logged output, as a string.
  """
  contents = xcresulttool_json('get', '--path', xcresult_path, '--id', log_id)

  result = []
  collect_log_output(contents, result)
  return ''.join(result)


def collect_log_output(activity_log, result):
  """Recursively collects emitted output from the activity log.

  Args:
    activity_log: Parsed JSON of an xcresult activity log.
    result: An array into which all log data should be appended.
  """
  output = activity_log.get('emittedOutput')
  if output:
    result.append(output['_value'])
  else:
    subsections = activity_log.get('subsections')
    if subsections:
      for subsection in subsections['_values']:
        collect_log_output(subsection, result)


def xcresulttool(*args):
  """Runs xcresulttool and returns its output as a string."""
  cmd = ['xcrun', 'xcresulttool']
  cmd.extend(args)

  return subprocess.check_output(cmd)


def xcresulttool_json(*args):
  """Runs xcresulttool and its output as parsed JSON."""
  args = list(args) + ['--format', 'json']
  contents = xcresulttool(*args)
  return json.loads(contents)


if __name__ == '__main__':
  main()
