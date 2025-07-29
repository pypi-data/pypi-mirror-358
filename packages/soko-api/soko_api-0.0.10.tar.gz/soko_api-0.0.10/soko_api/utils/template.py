import re
import datetime

KEY_PATTERN = re.compile(r"(\{.*?[^{0]*\})")
OPTIONAL_PATTERN = re.compile(r"(<.*?[^{0]*>)[^0-9]*?")
ROOT_PATTERN = re.compile(r"(\{root.*?[^{0]*\})")


def get_datetime_data(datetime_obj=None):
    """Returns current datetime data as dictionary.

    Args:
        datetime_obj (datetime): Specific datetime object

    Returns:
        dict: prepared date & time data

    Available keys:
        "d" - <Day of month number> in shortest possible way.
        "dd" - <Day of month number> with 2 digits.
        "ddd" - <Week day name> shortened week day. e.g.: `Mon`, ...
        "dddd" - <Week day name> full name of week day. e.g.: `Monday`, ...
        "m" - <Month number> in shortest possible way. e.g.: `1` if January
        "mm" - <Month number> with 2 digits.
        "mmm" - <Month name> shortened month name. e.g.: `Jan`, ...
        "mmmm" - <Month name> full month name. e.g.: `January`, ...
        "yy" - <Year number> shortened year. e.g.: `19`, `20`, ...
        "yyyy" - <Year number> full year. e.g.: `2019`, `2020`, ...
        "H" - <Hours number 24-hour> shortened hours.
        "HH" - <Hours number 24-hour> with 2 digits.
        "h" - <Hours number 12-hour> shortened hours.
        "hh" - <Hours number 12-hour> with 2 digits.
        "ht" - <Midday type> AM or PM.
        "M" - <Minutes number> shortened minutes.
        "MM" - <Minutes number> with 2 digits.
        "S" - <Seconds number> shortened seconds.
        "SS" - <Seconds number> with 2 digits.
    """

    if not datetime_obj:
        datetime_obj = datetime.datetime.now()

    year = datetime_obj.strftime("%Y")

    month = datetime_obj.strftime("%m")
    month_name_full = datetime_obj.strftime("%B")
    month_name_short = datetime_obj.strftime("%b")
    day = datetime_obj.strftime("%d")

    weekday_full = datetime_obj.strftime("%A")
    weekday_short = datetime_obj.strftime("%a")

    hours = datetime_obj.strftime("%H")
    hours_midday = datetime_obj.strftime("%I")
    hour_midday_type = datetime_obj.strftime("%p")
    minutes = datetime_obj.strftime("%M")
    seconds = datetime_obj.strftime("%S")

    return {
        "d": str(int(day)),
        "dd": str(day),
        "ddd": weekday_short,
        "dddd": weekday_full,
        "m": str(int(month)),
        "mm": str(month),
        "mmm": month_name_short,
        "mmmm": month_name_full,
        "yy": str(year[2:]),
        "yyyy": str(year),
        "H": str(int(hours)),
        "HH": str(hours),
        "h": str(int(hours_midday)),
        "hh": str(hours_midday),
        "ht": hour_midday_type,
        "M": str(int(minutes)),
        "MM": str(minutes),
        "S": str(int(seconds)),
        "SS": str(seconds),
    }


def build_template_data(user, project, folder, pathData, version=None, output=None):
    hierarchy = pathData["folderPath"].split('/')
    hierarchy = hierarchy[1:-2]

    formatData = {
        'studio': {
            'name': '',
            'code': ''
        },
        'user': user["user_metadata"]["user_name"],
        'project': {
            'name': project["name"],
            'code': project["codeName"] if project["codeName"] else project["name"]
        },
        'folder': folder["parent"],  # asset
        'username': user["user_metadata"]["user_name"],
        'asset': folder["parent"]["name"],  # parent
        'family': output["outputType"]["name"] if output and output["outputType"] else None,
        'subset': output["output"]["name"] if output else None,
        'version': version["versionNumber"] if version else 1,
        'hierarchy': '/'.join(hierarchy),
        'parent': folder["parent"]["parent"]["name"],  # parent of parent
        'task': {
            'name': folder["name"],
            'type': folder["type"]["name"],
            'short': folder["shortName"]
        }
    }

    datetimeData = get_datetime_data()

    templateData = formatData | datetimeData
    return templateData


def parse_templates(templates, template_data):
    parsed_templates = []
    for template in templates:
        res = {}
        for k, v in template.items():
            parsed_template = parse_template(template[k], template_data)
            res[k] = parsed_template
        parsed_templates.append(res)

    return parsed_templates

def parse_template(template, template_data):
    REG_EXP = r"\[([^)]+)\]"

    variables = re.findall(KEY_PATTERN, template)

    variable_values = []
    for match in variables:
        key = match.replace("{", "").replace("}", "").lower()

        variable_value = {
            'variable': match,
            'value': None
        }

        matches = re.search(REG_EXP, match)
        if matches:
            key = key.replace(matches.group(), "")
            variable_object = template_data.get(key)
            if variable_object:
                prop = variable_object.get(matches.group(1))
                variable_value["value"] = prop

        else:
            if template_data.get(key) is not None:
                if isinstance(template_data.get(key), str):
                    if match.isupper():  # startsWithCapital
                        variable_value["value"] = template_data.get(key).capitalize()
                    else:
                        variable_value["value"] = template_data.get(key)
                else:
                    if template_data.get(key, {}).get("name") is not None:
                        if match.isupper(): # startsWithCapital
                            variable_value["value"] = template_data.get(key, {}).get("name").capitalize()
                        else:
                            variable_value["value"] = template_data.get(key, {}).get("name")
                    else:
                        variable_value["value"] = match
            else:
                variable_value["value"] = match

        variable_values.append(variable_value)

    VARIANT_RE = r"/_?{variant}*_?/gi"

    for variable in variable_values:
        if variable.get("value") is not None:
            template = template.replace(variable.get("variable"), variable.get("value"))

        # remove variant with optional lead/follow "_" char if not provided
        if variable.get("variable", "").lower() == '{variant}' and variable.get("value", "").lower() == '{variant}':
            # template = template.replace(regex, "")
            template = re.sub(VARIANT_RE, "", template)

    optional_variables = re.findall(OPTIONAL_PATTERN, template)

    for variable in optional_variables:
        if "{" in variable:
            if "@frame" in variable:
                pass
            else:
                template = template.replace(variable, "")
        else:
            template = template.replace(variable, variable.replace("<", "").replace(">", ""))

    return template

def parse_root(template, roots):

    REG_EXP = r"\[([^)]+)\]"

    variables = re.findall(ROOT_PATTERN, template)

    parsed_templates = []
    for match in variables:
        key = match.replace("{", "").replace("}", "").lower()

        matches = re.search(REG_EXP, match)
        if matches:
            key = key.replace(matches.group(), "")
            root = [r for r in roots if r["name"] == matches.group(1)]

            if root:
                root = root[0]

            if not root:
                try:
                    root = roots[0]
                except:
                    pass

            if not root:
                raise Exception("Cannot find root!")

            parsed_templates.append({
                'path': template.replace(match, root.get('windows')),
                'os': "windows",
                'prefixVariable': match.replace("{", "").replace("}", ""),
                'prefix': root.get('windows')
            })

            parsed_templates.append({
                'path': template.replace(match, root.get('darwin')),
                'os': "darwin",
                'prefixVariable': match.replace("{", "").replace("}", ""),
                'prefix': root.get('darwin')
            })

            parsed_templates.append({
                'path': template.replace(match, root.get('linux')),
                'os': "linux",
                'prefixVariable': match.replace("{", "").replace("}", ""),
                'prefix': root.get('linux')
            })

    return parsed_templates