# coding: UTF-8
import sys
bstack1l1l11l_opy_ = sys.version_info [0] == 2
bstack1ll11l_opy_ = 2048
bstack1l11ll1_opy_ = 7
def bstack1l1ll1_opy_ (bstack111ll1l_opy_):
    global bstack111ll1_opy_
    bstack11ll1ll_opy_ = ord (bstack111ll1l_opy_ [-1])
    bstack1l11ll_opy_ = bstack111ll1l_opy_ [:-1]
    bstack11l1l11_opy_ = bstack11ll1ll_opy_ % len (bstack1l11ll_opy_)
    bstack11ll1_opy_ = bstack1l11ll_opy_ [:bstack11l1l11_opy_] + bstack1l11ll_opy_ [bstack11l1l11_opy_:]
    if bstack1l1l11l_opy_:
        bstack111ll11_opy_ = unicode () .join ([unichr (ord (char) - bstack1ll11l_opy_ - (bstack1l1l1ll_opy_ + bstack11ll1ll_opy_) % bstack1l11ll1_opy_) for bstack1l1l1ll_opy_, char in enumerate (bstack11ll1_opy_)])
    else:
        bstack111ll11_opy_ = str () .join ([chr (ord (char) - bstack1ll11l_opy_ - (bstack1l1l1ll_opy_ + bstack11ll1ll_opy_) % bstack1l11ll1_opy_) for bstack1l1l1ll_opy_, char in enumerate (bstack11ll1_opy_)])
    return eval (bstack111ll11_opy_)
import threading
import os
import logging
from uuid import uuid4
from bstack_utils.bstack111llll1l1_opy_ import bstack111ll1l111_opy_, bstack111lll11l1_opy_
from bstack_utils.bstack111ll1lll1_opy_ import bstack111l1ll1l_opy_
from bstack_utils.helper import bstack11l1ll11ll_opy_, bstack1llllll1l_opy_, Result
from bstack_utils.bstack111lll1lll_opy_ import bstack1l1lll1l_opy_
from bstack_utils.capture import bstack111lll1111_opy_
from bstack_utils.constants import *
logger = logging.getLogger(__name__)
class bstack1l11l1l1l1_opy_:
    def __init__(self):
        self.bstack111llllll1_opy_ = bstack111lll1111_opy_(self.bstack111llll1ll_opy_)
        self.tests = {}
    @staticmethod
    def bstack111llll1ll_opy_(log):
        if not (log[bstack1l1ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ໵")] and log[bstack1l1ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ໶")].strip()):
            return
        active = bstack111l1ll1l_opy_.bstack111ll1llll_opy_()
        log = {
            bstack1l1ll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ໷"): log[bstack1l1ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩ໸")],
            bstack1l1ll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ໹"): bstack1llllll1l_opy_(),
            bstack1l1ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭໺"): log[bstack1l1ll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ໻")],
        }
        if active:
            if active[bstack1l1ll1_opy_ (u"ࠧࡵࡻࡳࡩࠬ໼")] == bstack1l1ll1_opy_ (u"ࠨࡪࡲࡳࡰ࠭໽"):
                log[bstack1l1ll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ໾")] = active[bstack1l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ໿")]
            elif active[bstack1l1ll1_opy_ (u"ࠫࡹࡿࡰࡦࠩༀ")] == bstack1l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࠪ༁"):
                log[bstack1l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭༂")] = active[bstack1l1ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ༃")]
        bstack1l1lll1l_opy_.bstack11llll1l1_opy_([log])
    def start_test(self, attrs):
        test_uuid = uuid4().__str__()
        self.tests[test_uuid] = {}
        self.bstack111llllll1_opy_.start()
        driver = bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧ༄"), None)
        bstack111llll1l1_opy_ = bstack111lll11l1_opy_(
            name=attrs.scenario.name,
            uuid=test_uuid,
            started_at=bstack1llllll1l_opy_(),
            file_path=attrs.feature.filename,
            result=bstack1l1ll1_opy_ (u"ࠤࡳࡩࡳࡪࡩ࡯ࡩࠥ༅"),
            framework=bstack1l1ll1_opy_ (u"ࠪࡆࡪ࡮ࡡࡷࡧࠪ༆"),
            scope=[attrs.feature.name],
            bstack111ll1l1ll_opy_=bstack1l1lll1l_opy_.bstack111ll11ll1_opy_(driver) if driver and driver.session_id else {},
            meta={},
            tags=attrs.scenario.tags
        )
        self.tests[test_uuid][bstack1l1ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ༇")] = bstack111llll1l1_opy_
        threading.current_thread().current_test_uuid = test_uuid
        bstack1l1lll1l_opy_.bstack111llll111_opy_(bstack1l1ll1_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭༈"), bstack111llll1l1_opy_)
    def end_test(self, attrs):
        bstack111lll1l11_opy_ = {
            bstack1l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦ༉"): attrs.feature.name,
            bstack1l1ll1_opy_ (u"ࠢࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠧ༊"): attrs.feature.description
        }
        current_test_uuid = threading.current_thread().current_test_uuid
        bstack111llll1l1_opy_ = self.tests[current_test_uuid][bstack1l1ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ་")]
        meta = {
            bstack1l1ll1_opy_ (u"ࠤࡩࡩࡦࡺࡵࡳࡧࠥ༌"): bstack111lll1l11_opy_,
            bstack1l1ll1_opy_ (u"ࠥࡷࡹ࡫ࡰࡴࠤ།"): bstack111llll1l1_opy_.meta.get(bstack1l1ll1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ༎"), []),
            bstack1l1ll1_opy_ (u"ࠧࡹࡣࡦࡰࡤࡶ࡮ࡵࠢ༏"): {
                bstack1l1ll1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦ༐"): attrs.feature.scenarios[0].name if len(attrs.feature.scenarios) else None
            }
        }
        bstack111llll1l1_opy_.bstack111lll1l1l_opy_(meta)
        bstack111llll1l1_opy_.bstack111llll11l_opy_(bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࠬ༑"), []))
        bstack111ll1l1l1_opy_, exception = self._111ll1ll11_opy_(attrs)
        bstack111lll11ll_opy_ = Result(result=attrs.status.name, exception=exception, bstack111lll1ll1_opy_=[bstack111ll1l1l1_opy_])
        self.tests[threading.current_thread().current_test_uuid][bstack1l1ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ༒")].stop(time=bstack1llllll1l_opy_(), duration=int(attrs.duration)*1000, result=bstack111lll11ll_opy_)
        bstack1l1lll1l_opy_.bstack111llll111_opy_(bstack1l1ll1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ༓"), self.tests[threading.current_thread().current_test_uuid][bstack1l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭༔")])
    def bstack111ll11ll_opy_(self, attrs):
        bstack111ll1ll1l_opy_ = {
            bstack1l1ll1_opy_ (u"ࠫ࡮ࡪࠧ༕"): uuid4().__str__(),
            bstack1l1ll1_opy_ (u"ࠬࡱࡥࡺࡹࡲࡶࡩ࠭༖"): attrs.keyword,
            bstack1l1ll1_opy_ (u"࠭ࡳࡵࡧࡳࡣࡦࡸࡧࡶ࡯ࡨࡲࡹ࠭༗"): [],
            bstack1l1ll1_opy_ (u"ࠧࡵࡧࡻࡸ༘ࠬ"): attrs.name,
            bstack1l1ll1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸ༙ࠬ"): bstack1llllll1l_opy_(),
            bstack1l1ll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ༚"): bstack1l1ll1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ༛"),
            bstack1l1ll1_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩ༜"): bstack1l1ll1_opy_ (u"ࠬ࠭༝")
        }
        self.tests[threading.current_thread().current_test_uuid][bstack1l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ༞")].add_step(bstack111ll1ll1l_opy_)
        threading.current_thread().current_step_uuid = bstack111ll1ll1l_opy_[bstack1l1ll1_opy_ (u"ࠧࡪࡦࠪ༟")]
    def bstack1l111ll1ll_opy_(self, attrs):
        current_test_id = bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ༠"), None)
        current_step_uuid = bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡷࡹ࡫ࡰࡠࡷࡸ࡭ࡩ࠭༡"), None)
        bstack111ll1l1l1_opy_, exception = self._111ll1ll11_opy_(attrs)
        bstack111lll11ll_opy_ = Result(result=attrs.status.name, exception=exception, bstack111lll1ll1_opy_=[bstack111ll1l1l1_opy_])
        self.tests[current_test_id][bstack1l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭༢")].bstack111ll1l11l_opy_(current_step_uuid, duration=int(attrs.duration)*1000, result=bstack111lll11ll_opy_)
        threading.current_thread().current_step_uuid = None
    def bstack111ll1ll1_opy_(self, name, attrs):
        try:
            bstack111lllll11_opy_ = uuid4().__str__()
            self.tests[bstack111lllll11_opy_] = {}
            self.bstack111llllll1_opy_.start()
            scopes = []
            driver = bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪ༣"), None)
            current_thread = threading.current_thread()
            if not hasattr(current_thread, bstack1l1ll1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪ༤")):
                current_thread.current_test_hooks = []
            current_thread.current_test_hooks.append(bstack111lllll11_opy_)
            if name in [bstack1l1ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠥ༥"), bstack1l1ll1_opy_ (u"ࠢࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠥ༦")]:
                file_path = os.path.join(attrs.config.base_dir, attrs.config.environment_file)
                scopes = [attrs.config.environment_file]
            elif name in [bstack1l1ll1_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡨࡨࡥࡹࡻࡲࡦࠤ༧"), bstack1l1ll1_opy_ (u"ࠤࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠤ༨")]:
                file_path = attrs.filename
                scopes = [attrs.name]
            else:
                file_path = attrs.filename
                if hasattr(attrs, bstack1l1ll1_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࠫ༩")):
                    scopes =  [attrs.feature.name]
            hook_data = bstack111ll1l111_opy_(
                name=name,
                uuid=bstack111lllll11_opy_,
                started_at=bstack1llllll1l_opy_(),
                file_path=file_path,
                framework=bstack1l1ll1_opy_ (u"ࠦࡇ࡫ࡨࡢࡸࡨࠦ༪"),
                bstack111ll1l1ll_opy_=bstack1l1lll1l_opy_.bstack111ll11ll1_opy_(driver) if driver and driver.session_id else {},
                scope=scopes,
                result=bstack1l1ll1_opy_ (u"ࠧࡶࡥ࡯ࡦ࡬ࡲ࡬ࠨ༫"),
                hook_type=name
            )
            self.tests[bstack111lllll11_opy_][bstack1l1ll1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡩࡧࡴࡢࠤ༬")] = hook_data
            current_test_id = bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠢࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠦ༭"), None)
            if current_test_id:
                hook_data.bstack111ll11lll_opy_(current_test_id)
            if name == bstack1l1ll1_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧ༮"):
                threading.current_thread().before_all_hook_uuid = bstack111lllll11_opy_
            threading.current_thread().current_hook_uuid = bstack111lllll11_opy_
            bstack1l1lll1l_opy_.bstack111llll111_opy_(bstack1l1ll1_opy_ (u"ࠤࡋࡳࡴࡱࡒࡶࡰࡖࡸࡦࡸࡴࡦࡦࠥ༯"), hook_data)
        except Exception as e:
            logger.debug(bstack1l1ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡲࡧࡨࡻࡲࡳࡧࡧࠤ࡮ࡴࠠࡴࡶࡤࡶࡹࠦࡨࡰࡱ࡮ࠤࡪࡼࡥ࡯ࡶࡶ࠰ࠥ࡮࡯ࡰ࡭ࠣࡲࡦࡳࡥ࠻ࠢࠨࡷ࠱ࠦࡥࡳࡴࡲࡶ࠿ࠦࠥࡴࠤ༰"), name, e)
    def bstack11l1lllll_opy_(self, attrs):
        bstack111lll111l_opy_ = bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ༱"), None)
        hook_data = self.tests[bstack111lll111l_opy_][bstack1l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ༲")]
        status = bstack1l1ll1_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨ༳")
        exception = None
        bstack111ll1l1l1_opy_ = None
        if hook_data.name == bstack1l1ll1_opy_ (u"ࠢࡢࡨࡷࡩࡷࡥࡡ࡭࡮ࠥ༴"):
            self.bstack111llllll1_opy_.reset()
            bstack111lllll1l_opy_ = self.tests[bstack11l1ll11ll_opy_(threading.current_thread(), bstack1l1ll1_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ༵"), None)][bstack1l1ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ༶")].result.result
            if bstack111lllll1l_opy_ == bstack1l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦ༷ࠥ"):
                if attrs.hook_failures == 1:
                    status = bstack1l1ll1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ༸")
                elif attrs.hook_failures == 2:
                    status = bstack1l1ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨ༹ࠧ")
            elif attrs.aborted:
                status = bstack1l1ll1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ༺")
            threading.current_thread().before_all_hook_uuid = None
        else:
            if hook_data.name == bstack1l1ll1_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࠫ༻") and attrs.hook_failures == 1:
                status = bstack1l1ll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ༼")
            elif hasattr(attrs, bstack1l1ll1_opy_ (u"ࠩࡨࡶࡷࡵࡲࡠ࡯ࡨࡷࡸࡧࡧࡦࠩ༽")) and attrs.error_message:
                status = bstack1l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ༾")
            bstack111ll1l1l1_opy_, exception = self._111ll1ll11_opy_(attrs)
        bstack111lll11ll_opy_ = Result(result=status, exception=exception, bstack111lll1ll1_opy_=[bstack111ll1l1l1_opy_])
        hook_data.stop(time=bstack1llllll1l_opy_(), duration=0, result=bstack111lll11ll_opy_)
        bstack1l1lll1l_opy_.bstack111llll111_opy_(bstack1l1ll1_opy_ (u"ࠫࡍࡵ࡯࡬ࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭༿"), self.tests[bstack111lll111l_opy_][bstack1l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨཀ")])
        threading.current_thread().current_hook_uuid = None
    def _111ll1ll11_opy_(self, attrs):
        try:
            import traceback
            bstack11l111ll1l_opy_ = traceback.format_tb(attrs.exc_traceback)
            bstack111ll1l1l1_opy_ = bstack11l111ll1l_opy_[-1] if bstack11l111ll1l_opy_ else None
            exception = attrs.exception
        except Exception:
            logger.debug(bstack1l1ll1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡵࡣࡤࡷࡵࡶࡪࡪࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡤࡷࡶࡸࡴࡳࠠࡵࡴࡤࡧࡪࡨࡡࡤ࡭ࠥཁ"))
            bstack111ll1l1l1_opy_ = None
            exception = None
        return bstack111ll1l1l1_opy_, exception