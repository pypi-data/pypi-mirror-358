#
#   Module used to invoke R code using a Rscript subprocess and
#   passing parameters to, and receiving results from, R functions through
#   temporary JSON files
#
from subprocess import Popen, PIPE
from random import random
from json import dump, load
from os import remove

R_SCRIPT = 'Rscript call\\R\\main.R {}'
R_TMP_FILE = 'call/R/tmp/{}.{}'
SUPPORTED = {'test': ['echo', 'error'],
             'bnlearn': ['dagscore', 'citest', 'pdag2cpdag', 'shd', 'learn',
                         'compare', 'import']}


def dispatch_r(package, method, params=None):
    """
        Dispatch a request to R code

        :param str package: R "package" to use
        :param str method: the R function to call in the package
        :param dict params: parameters for the R function

        :raises TypeError: if arguments not of correct type
        :raises ValueError: if unsupported package/method requested
        :raises RuntimeError: if R code ends abnormally

        :returns tuple: (return from R function, R stdout)
    """
    if not isinstance(package, str) or not isinstance(method, str) \
            or (params is not None and not isinstance(params, dict)):
        raise TypeError('dispatch_r called with bad arg types')

    if package not in SUPPORTED or method not in SUPPORTED[package] \
            or params == {}:
        raise ValueError('dispatch_r called with bad arg values')

    # Serialise package, method and params as a JSON structure and write
    # to temporary file

    id = int(random() * 10000000)
    json_args = {'package': package, 'method': method, 'params': params}
    infile = R_TMP_FILE.format(id, 'in.json')
    with open(infile, 'w', encoding='utf-8') as f:
        dump(json_args, f, ensure_ascii=False, indent=4)

    # run R entry point script as a subprocess and capture stdout and stderr

    r = Popen(R_SCRIPT.format(id), shell=True, stdout=PIPE, stderr=PIPE)
    stdout = [ln.decode('UTF-8')[0:-2] for ln in r.stdout if len(ln)]
    # print('\n\nR method {}.{} ({}) stdout:\n{}'
    #       .format(package, method, id, '\n'.join(stdout)))
    stderr = [ln.decode('UTF-8')[0:-2] for ln in r.stderr if len(ln)]
    # print('\nR stderr: {}\n<ends>\n'.format('\n'.join(stderr)))

    # stderr should be empty if no errors occurred in R subprocess

    if len(stderr):
        remove(infile)
        raise RuntimeError('R code abend for id {}: {}'.format(id, stderr))

    # R script will have written its return values to a temporary JSON file
    # which we deserialise and return

    outfile = R_TMP_FILE.format(id, 'out.json')
    with open(outfile, 'r', encoding='utf-8') as f:
        result = load(f)

    # print('result: {}'.format(result))

    remove(infile)
    remove(outfile)

    return (result, stdout)


if __name__ == '__main__':
    dispatch_r('test', 'echo', {'alpha': 0.5})
