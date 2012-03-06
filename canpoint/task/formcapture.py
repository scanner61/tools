# -*- coding: utf-8 -*-

"""
    task.formcapture
   ~~~~~~~~~~~~~~~~~

    HTMLファイルの画面ハードコピーを取る。
"""

import subprocess
import urllib
import os, platform
import errno, signal
import time
from image import triming

CREATE_NO_WINDOW = 0x8000000

import logging
import traceback
logger = logging.getLogger(__file__)


IS_WINDOWS = (os.name == 'nt')


def generate_capture(exepath, html_path, img_path):
    """  HTML画面キャプチャを取得し、png形式で出力。

    * exepath: コマンド
    * html_path: HTMLファイルパス
    * img_path: 結果出力パス
    """

    timeout = 10

    try:
        if IS_WINDOWS:
            page_uri = 'file:%s' % urllib.pathname2url(os.path.normpath(html_path))
            exepath += '.exe'
            cmd = [exepath, '--url=%s' % page_uri, '--out=%s' % img_path, '--max-wait=%s' % 30000]
            proc = subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW, bufsize=-1)
        else:
            page_uri = 'file://%s' % urllib.pathname2url(os.path.normpath(html_path))
            exepath += '64' if '64' in platform.machine() else ''
            #if os.getenv('DISPLAY'):
            cmd = [exepath, '--url=%s' % page_uri, '--out=%s' % img_path, '--max-wait=%s' % 30000]
            #else:
            #    cmd = ['xvfb-run', '-s', '-screen 0, 1024x768x24', exepath, '--url=%s' % page_uri, '--out=%s' % img_path]
            proc = subprocess.Popen(cmd, bufsize=-1)
        st = time.time()
        while time.time() - st <= timeout:
            if proc.poll() is not None:
                try:
                    triming(img_path)
                except:
                    raise
                finally:
                    return True
            else:
                time.sleep(0.1)

        logger.debug('dead process %s' % proc.pid)
        try:
            proc.terminate()
        except:
            logger.debug(traceback.format_exc())

        time.sleep(1)
        if proc.poll() is not None:
            try:
                proc.kill()
            except:
                logger.debug(traceback.format_exc())

        return False
    except:
        logger.debug(traceback.format_exc())
        #logger.debug('exepath = %s' % (exepath))
        #logger.debug('Error occured while tring to generate capture for %s -> %s' % (html_path, img_path))
        raise


def vfb(display_spec="1024x768x24", server=0, screen=0, auto_screen=True):
    """ run Xvfb and set DISPLAY env
    """

    while True:
        try:
            devnull = open("/dev/null", "w")
            proc = subprocess.Popen(["Xvfb", ":%d" % server, "-screen", "%d" % screen, display_spec],
                                    shell=False, stdout=devnull, stderr=devnull)
            os.environ["DISPLAY"] = ":%d.%d" % (server, screen)
            return (proc, screen)
        except:
            logger.debug(traceback.format_exc())
            if not auto_screen:
                break
            screen += 1


from functools import wraps

def xvfb(f):
    """ヘッドレスでGUI環境を立ち上げる"""
    @wraps(f)
    def func(*args, **kws):
        if not IS_WINDOWS:
            p, s = vfb()

        f(*args, **kws)

        if not IS_WINDOWS:
            p.terminate()

    return func

