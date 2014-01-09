<?php
# Source:
# http://stackoverflow.com/questions/4325224/doxygen-how-to-describe-class-member-variables-in-php
#

$source = file_get_contents($argv[1]);

// Makes the following:
// /**
//  * @var VarType
//  * @brief Description
//  */
// (public|protected|private|var) $paramName = 'value';
// 
// recongizable as valid variable documentation
$regexp = '#\@var\s+([^\s]+)([^/]+)/\s+(var|public|protected|private)\s+(\$[^\s;=]+)#';
$replac = '${2} */ ${3} ${1} ${4}';
$source = preg_replace($regexp, $replac, $source);


// Change the following:
// /** @param VarType[] $pParamName Description **/
// function name(array $pParamName) {

// Into:
// /** @param array $pParamName Description **/
// function name(VarType[] $pParamName) {
$regexp = '#\@param\s+([^\s]+)\[\]\s+(\$[^\s]+)\s+([^/]+)/\s+(public|protected|private)?\s+function\s+([^\s]+)\s*\(([^)]*)array\s+\2([^)]*)\)(\s+){#s';
$replac = '@param array ${2} ${3}/ ${4} function ${5} (${6} ${1}[] ${2}${7})${8}{';
$source = preg_replace($regexp, $replac, $source);


// Change the following:
// /** @param (bool|int|float|double|string) $pParamName Description **/
// function name($pParamName) {

// Into:
// /** @param (bool|int|float|double|string) $pParamName Description **/
// ReturnType function name((bool|int|float|double|string) $pParamName) {

function callback($matches) {

    $lines = explode("\n", $matches[2]);
    $return = '';
    $params = array();

    foreach($lines as $line) {
        $line = trim($line, "\t *");

        if (strpos($line, '@return') === 0) {
            $return = array_pop(array_filter(explode(' ', $line)));
            continue;
        }

        if (strpos($line, '@param') !== 0) {
            continue;
        }

        $tmp = array_filter(explode(' ', $line));
        # remove '@param'
        array_shift($tmp);
        $type = array_shift($tmp);
        $arg = array_shift($tmp);
        $params[] = "$type $arg";
    }

    $ret = $matches[1] . implode(',', $params) . $matches[3];
    if ($return) {
        $ret = str_replace('function', "$return function", $ret);
    }
    return $ret;
}
$regexp = '#(/\*\*' .
    '([^/]+?)' .
    '\*/\s+' .
    '(?:public|protected|private)\s+function\s+(?:[^\(\s]+?)\()(?:(?:[^,]*?\s*,?\s*)*)(\)\s+{)#mis';
#$regexp = '#\@param\s+(bool|int|float|double|string)\s+(\$[^\s]+)\s+([^/]+)/\s+(public|protected|private)?\s+function\s+([^\(\s]+)\s*([^)]*)(\(|,)\s*\2([^)]*)\)(\s+){#s';
$replac = '@param ${1} ${2} ${3}/ ${4} function ${5}${6}${7}${1} ${2}${8})${9}{ '; //${6}${1} ${2}${7})${8}{';
$source = preg_replace_callback($regexp, 'callback', $source);


echo $source;
