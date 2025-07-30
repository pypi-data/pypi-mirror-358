# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import os
from typing import NamedTuple, Tuple, Optional, Union, List
from parsley import makeGrammar

# https://peps.python.org/pep-0508/#complete-grammar
GRAMMAR = """
wsp            = ' ' | '\t'
version_cmp    = wsp* <'<=' | '<' | '!=' | '==' | '>=' | '>' | '~=' | '==='>
version        = wsp* <( letterOrDigit | '-' | '_' | '.' | '*' | '+' | '!' )+>
version_one    = version_cmp:op version:v wsp* -> (op, v)
version_many   = version_one:v1 (wsp* ',' version_one)*:v2 -> [v1] + v2
versionspec    = ('(' version_many:v ')' ->v) | version_many
urlspec        = '@' wsp* <URI_reference>
marker_op      = version_cmp | (wsp* 'in') | (wsp* 'not' wsp+ 'in')
python_str_c   = (wsp | letter | digit | '(' | ')' | '.' | '{' | '}' |
                 '-' | '_' | '*' | '#' | ':' | ';' | ',' | '/' | '?' |
                 '[' | ']' | '!' | '~' | '`' | '@' | '$' | '%' | '^' |
                 '&' | '=' | '+' | '|' | '<' | '>' )
dquote         = '"'
squote         = '\\''
python_str     = (squote <(python_str_c | dquote)*>:s squote |
                  dquote <(python_str_c | squote)*>:s dquote) -> s
env_var        = ( 'python_version' | 'python_full_version' | 'os_name' | 'sys_platform'
                 | 'platform_release' | 'platform_system' | 'platform_version' | 'platform_machine' | 'platform_python_implementation'
                 | 'implementation_name' | 'implementation_version' | 'extra' # ONLY when defined by a containing layer
                 )
marker_var     = wsp* (env_var | python_str)
marker_expr    = marker_var:l marker_op:o marker_var:r -> Marker(o, l, r)
               | wsp* '(' marker:m wsp* ')' -> m
marker_and     = marker_expr:l wsp* 'and' marker_expr:r -> Marker('and', l, r)
               | marker_expr:m -> m
marker_or      = marker_and:l wsp* 'or' marker_and:r -> Marker('or', l, r)
               | marker_and:m -> m
marker         = marker_or
quoted_marker  = ';' wsp* marker
identifier_end = letterOrDigit | (('-' | '_' | '.' )* letterOrDigit)
identifier     = < letterOrDigit identifier_end* >
name           = identifier
extras_list    = identifier:i (wsp* ',' wsp* identifier)*:ids -> [i] + ids
extras         = '[' wsp* extras_list?:e wsp* ']' -> e
name_req       = (name:n wsp* extras?:e wsp* versionspec?:v wsp* quoted_marker?:m    -> (n, e or [], v or [], m))
url_req        = (name:n wsp* extras?:e wsp* urlspec:v (wsp+ | end) quoted_marker?:m -> (n, e or [], v, m))
specification  = wsp* ( url_req | name_req ):s wsp* -> Spec(*s)

URI_reference = <URI | relative_ref>
URI           = scheme ':' hier_part ('?' query )? ('#' fragment)?
hier_part     = ('//' authority path_abempty) | path_absolute | path_rootless | path_empty
absolute_URI  = scheme ':' hier_part ( '?' query )?
relative_ref  = relative_part ( '?' query )? ('#' fragment)?
relative_part = '//' authority path_abempty | path_absolute | path_noscheme | path_empty
scheme        = letter ( letter | digit | '+' | '-' | '.')*
authority     = ( userinfo '@' )? host ( ':' port )?
userinfo      = ( unreserved | pct_encoded | sub_delims | ':')*
host          = IP_literal | IPv4address | reg_name
port          = digit*
IP_literal    = '[' ( IPv6address | IPvFuture) ']'
IPvFuture     = 'v' hexdig+ '.' ( unreserved | sub_delims | ':')+
IPv6address   = (
                  ( h16 ':'){6} ls32
                  | '::' ( h16 ':'){5} ls32
                  | ( h16 )?  '::' ( h16 ':'){4} ls32
                  | ( ( h16 ':')? h16 )? '::' ( h16 ':'){3} ls32
                  | ( ( h16 ':'){0,2} h16 )? '::' ( h16 ':'){2} ls32
                  | ( ( h16 ':'){0,3} h16 )? '::' h16 ':' ls32
                  | ( ( h16 ':'){0,4} h16 )? '::' ls32
                  | ( ( h16 ':'){0,5} h16 )? '::' h16
                  | ( ( h16 ':'){0,6} h16 )? '::' )
h16           = hexdig{1,4}
ls32          = ( h16 ':' h16) | IPv4address
IPv4address   = dec_octet '.' dec_octet '.' dec_octet '.' dec_octet
nz            = ~'0' digit
dec_octet     = (
                  digit # 0-9
                  | nz digit # 10-99
                  | '1' digit{2} # 100-199
                  | '2' ('0' | '1' | '2' | '3' | '4') digit    # 200-249
                  | '25' ('0' | '1' | '2' | '3' | '4' | '5') ) # %250-255
reg_name = (unreserved | pct_encoded | sub_delims)*
path = ( path_abempty  # begins with '/' or is empty
       | path_absolute # begins with '/' but not '//'
       | path_noscheme # begins with a non-colon segment
       | path_rootless # begins with a segment
       | path_empty )  # zero characters
path_abempty  = ('/' segment)*
path_absolute = '/' (segment_nz ('/' segment)* )?
path_noscheme = segment_nz_nc ('/' segment)*
path_rootless = segment_nz ('/' segment)*
path_empty    = pchar{0}
segment       = pchar*
segment_nz    = pchar+
segment_nz_nc = ( unreserved | pct_encoded | sub_delims | '@')+ # non-zero-length segment without any colon ':'
pchar         = unreserved | pct_encoded | sub_delims | ':' | '@'
query         = ( pchar | '/' | '?')*
fragment      = ( pchar | '/' | '?')*
pct_encoded   = '%' hexdig
unreserved    = letter | digit | '-' | '.' | '_' | '~'
reserved      = gen_delims | sub_delims
gen_delims    = ':' | '/' | '?' | '#' | '(' | ')?' | '@'
sub_delims    = '!' | '$' | '&' | '\\'' | '(' | ')' | '*' | '+' | ',' | ';' | '='
hexdig        = digit | 'a' | 'A' | 'b' | 'B' | 'c' | 'C' | 'd' | 'D' | 'e' | 'E' | 'f' | 'F'
"""


class Marker(NamedTuple):
    op: str
    v1: Union[str, "Marker"]
    v2: Union[str, "Marker"]

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        out = ""

        if isinstance(self.v1, Marker):
            out += "( " + str(self.v1) + " )"
        else:
            out += self.v1

        out += " " + self.op + " "

        if isinstance(self.v2, Marker):
            out += "( " + str(self.v2) + " )"
        else:
            out += '"' + self.v2 + '"'

        return out


class Spec(NamedTuple):
    name: str
    extras: List[str]
    version: List[Tuple[str, str]]
    marker: Optional[Marker]

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        out = self.name
        if len(self.extras) > 0:
            out += "[" + ",".join(self.extras) + "]"
        out += " "
        if isinstance(self.version, str):
            out += "@ " + self.version
        else:
            out += ",".join([v[0] + v[1] for v in self.version])
        if self.marker is not None:
            out += " ; " + str(self.marker)
        return out


Parse = makeGrammar(GRAMMAR, {'Spec': Spec, 'Marker': Marker}, name = "PEP508")


def parse_line(line: str) -> Spec:
    return Parse(line).specification()


def parse_lines(lines: "list[str]") -> "(dict[str, Spec], list[str], str)":
    """
    Processes dependency requirement lines.

    Args:
        lines (list[str]): list of dependencies and (extra) index urls.

    Returns:
        (dict[str, Spec], list[str]): dictionary that contains the dependency specifcations and a list of (extra) index urls.

    Raises:
        AssertionError: if the lines contain invalid dependency specifications.
    """
    dependencies = {}
    invalid_lines = []
    extra_index = []
    index_url = None
    lines = map(lambda row: row.strip(), lines)
    lines = filter(lambda row: row != "" and not row.startswith("#"), lines)
    for line in lines:
        if line.startswith('--index-url'):
            index_url = line
            continue
        if line.startswith('--extra-index-url'):
            extra_index.append(line)
            continue
        try:
            spec: Spec = parse_line(line)
            dependencies[spec.name] = spec
        except Exception as e:
            invalid_lines.append(f"{line}\n{e}")
    if len(invalid_lines) > 0:
        raise AssertionError('\n'.join(invalid_lines))
    return (dependencies, extra_index, index_url)


def parse_requirements(requirements_path: Union[str, os.PathLike]) -> "(dict[str, Spec], list[str], str)":
    """
    Processes a requirements.txt file line-by-line.

    Args:
        requirements_path: Union[str, os.PathLike]: path to the requirements.txt file.

    Returns:
        (dict[str, Spec], list[str]): dictionary that contains the dependency specifcations and a list of (extra) index urls.

    Raises:
        AssertionError: if the lines contain invalid dependency specifications.
    """
    with open(requirements_path, "r") as f:
        lines = f.readlines()
        try:
            return parse_lines(lines)
        except AssertionError as err:
            raise AssertionError(f"Requirements file '{requirements_path}' contains invalid dependency specifications:\n{str(err)}")
