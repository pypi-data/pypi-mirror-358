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
import json
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1lllllll11l_opy_ import (
    bstack1lllll1lll1_opy_,
    bstack1111111ll1_opy_,
    bstack111111l1l1_opy_,
    bstack1111111l1l_opy_,
    bstack1lllll1l1l1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1ll1ll111ll_opy_ import bstack1lll1l1l1ll_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_, bstack1ll1llllll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll111111l1_opy_ import bstack1ll11111111_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1lll11111_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1llll1l1ll1_opy_(bstack1ll11111111_opy_):
    bstack1l1l11111l1_opy_ = bstack1l1ll1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡷ࡯ࡶࡦࡴࡶࠦ፶")
    bstack1l1ll11ll11_opy_ = bstack1l1ll1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧ፷")
    bstack1l1l111llll_opy_ = bstack1l1ll1_opy_ (u"ࠢ࡯ࡱࡱࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤ፸")
    bstack1l1l1111l1l_opy_ = bstack1l1ll1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣ፹")
    bstack1l1l1111lll_opy_ = bstack1l1ll1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡠࡴࡨࡪࡸࠨ፺")
    bstack1l1l1ll1ll1_opy_ = bstack1l1ll1_opy_ (u"ࠥࡧࡧࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡥࡵࡩࡦࡺࡥࡥࠤ፻")
    bstack1l1l11l11ll_opy_ = bstack1l1ll1_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡱࡥࡲ࡫ࠢ፼")
    bstack1l1l111lll1_opy_ = bstack1l1ll1_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡷࡹࡧࡴࡶࡵࠥ፽")
    def __init__(self):
        super().__init__(bstack1ll111111ll_opy_=self.bstack1l1l11111l1_opy_, frameworks=[bstack1lll1l1l1ll_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll11llll11_opy_((bstack1ll1llll111_opy_.BEFORE_EACH, bstack1ll1lllll1l_opy_.POST), self.bstack1l11l1ll1ll_opy_)
        TestFramework.bstack1ll11llll11_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1lllll1l_opy_.PRE), self.bstack1ll11ll111l_opy_)
        TestFramework.bstack1ll11llll11_opy_((bstack1ll1llll111_opy_.TEST, bstack1ll1lllll1l_opy_.POST), self.bstack1ll11l1llll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l1ll1ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llllll1_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1ll11111l_opy_ = self.bstack1l11ll11l1l_opy_(instance.context)
        if not bstack1l1ll11111l_opy_:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠨࡳࡦࡶࡢࡥࡨࡺࡩࡷࡧࡢࡨࡷ࡯ࡶࡦࡴࡶ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࠤ፾") + str(bstack1llllll1111_opy_) + bstack1l1ll1_opy_ (u"ࠢࠣ፿"))
        f.bstack1lllllll1ll_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1ll11ll11_opy_, bstack1l1ll11111l_opy_)
        bstack1l11l1lll11_opy_ = self.bstack1l11ll11l1l_opy_(instance.context, bstack1l11l1ll11l_opy_=False)
        f.bstack1lllllll1ll_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l111llll_opy_, bstack1l11l1lll11_opy_)
    def bstack1ll11ll111l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llllll1_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1ll1ll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        if not f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l11l11ll_opy_, False):
            self.__1l11ll11111_opy_(f,instance,bstack1llllll1111_opy_)
    def bstack1ll11l1llll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llllll1_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1ll1ll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        if not f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l11l11ll_opy_, False):
            self.__1l11ll11111_opy_(f, instance, bstack1llllll1111_opy_)
        if not f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l111lll1_opy_, False):
            self.__1l11l1ll1l1_opy_(f, instance, bstack1llllll1111_opy_)
    def bstack1l11l1llll1_opy_(
        self,
        f: bstack1lll1l1l1ll_opy_,
        driver: object,
        exec: Tuple[bstack1111111l1l_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1lllll1lll1_opy_, bstack1111111ll1_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1l1lllll1l1_opy_(instance):
            return
        if f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l111lll1_opy_, False):
            return
        driver.execute_script(
            bstack1l1ll1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂࠨᎀ").format(
                json.dumps(
                    {
                        bstack1l1ll1_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤᎁ"): bstack1l1ll1_opy_ (u"ࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨᎂ"),
                        bstack1l1ll1_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢᎃ"): {bstack1l1ll1_opy_ (u"ࠧࡹࡴࡢࡶࡸࡷࠧᎄ"): result},
                    }
                )
            )
        )
        f.bstack1lllllll1ll_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l111lll1_opy_, True)
    def bstack1l11ll11l1l_opy_(self, context: bstack1lllll1l1l1_opy_, bstack1l11l1ll11l_opy_= True):
        if bstack1l11l1ll11l_opy_:
            bstack1l1ll11111l_opy_ = self.bstack1l1lllll111_opy_(context, reverse=True)
        else:
            bstack1l1ll11111l_opy_ = self.bstack1l1llllll11_opy_(context, reverse=True)
        return [f for f in bstack1l1ll11111l_opy_ if f[1].state != bstack1lllll1lll1_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1ll1llllll_opy_, stage=STAGE.bstack1l1ll11ll1_opy_)
    def __1l11l1ll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llllll1_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1ll1_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦᎅ")).get(bstack1l1ll1_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦᎆ")):
            bstack1l1ll11111l_opy_ = f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1ll11ll11_opy_, [])
            if not bstack1l1ll11111l_opy_:
                self.logger.debug(bstack1l1ll1_opy_ (u"ࠣࡵࡨࡸࡤࡧࡣࡵ࡫ࡹࡩࡤࡪࡲࡪࡸࡨࡶࡸࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦᎇ") + str(bstack1llllll1111_opy_) + bstack1l1ll1_opy_ (u"ࠤࠥᎈ"))
                return
            driver = bstack1l1ll11111l_opy_[0][0]()
            status = f.bstack111111l111_opy_(instance, TestFramework.bstack1l1l111l11l_opy_, None)
            if not status:
                self.logger.debug(bstack1l1ll1_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡥࡴ࡬ࡺࡪࡸࡳ࠻ࠢࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧᎉ") + str(bstack1llllll1111_opy_) + bstack1l1ll1_opy_ (u"ࠦࠧᎊ"))
                return
            bstack1l1l11l11l1_opy_ = {bstack1l1ll1_opy_ (u"ࠧࡹࡴࡢࡶࡸࡷࠧᎋ"): status.lower()}
            bstack1l1l111l1ll_opy_ = f.bstack111111l111_opy_(instance, TestFramework.bstack1l1l11l1111_opy_, None)
            if status.lower() == bstack1l1ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᎌ") and bstack1l1l111l1ll_opy_ is not None:
                bstack1l1l11l11l1_opy_[bstack1l1ll1_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧᎍ")] = bstack1l1l111l1ll_opy_[0][bstack1l1ll1_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨࠫᎎ")][0] if isinstance(bstack1l1l111l1ll_opy_, list) else str(bstack1l1l111l1ll_opy_)
            driver.execute_script(
                bstack1l1ll1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠢᎏ").format(
                    json.dumps(
                        {
                            bstack1l1ll1_opy_ (u"ࠥࡥࡨࡺࡩࡰࡰࠥ᎐"): bstack1l1ll1_opy_ (u"ࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ᎑"),
                            bstack1l1ll1_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ᎒"): bstack1l1l11l11l1_opy_,
                        }
                    )
                )
            )
            f.bstack1lllllll1ll_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l111lll1_opy_, True)
    @measure(event_name=EVENTS.bstack1ll11ll1l1_opy_, stage=STAGE.bstack1l1ll11ll1_opy_)
    def __1l11ll11111_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llllll1_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1ll1_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦ᎓")).get(bstack1l1ll1_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ᎔")):
            test_name = f.bstack111111l111_opy_(instance, TestFramework.bstack1l11l1lll1l_opy_, None)
            if not test_name:
                self.logger.debug(bstack1l1ll1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡱ࡮ࡹࡳࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡱࡥࡲ࡫ࠢ᎕"))
                return
            bstack1l1ll11111l_opy_ = f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1ll11ll11_opy_, [])
            if not bstack1l1ll11111l_opy_:
                self.logger.debug(bstack1l1ll1_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡤࡳ࡫ࡹࡩࡷࡹ࠺ࠡࡰࡲࠤࡸࡺࡡࡵࡷࡶࠤ࡫ࡵࡲࠡࡶࡨࡷࡹ࠲ࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦ᎖") + str(bstack1llllll1111_opy_) + bstack1l1ll1_opy_ (u"ࠥࠦ᎗"))
                return
            for bstack1l1l1l1l1ll_opy_, bstack1l11ll111ll_opy_ in bstack1l1ll11111l_opy_:
                if not bstack1lll1l1l1ll_opy_.bstack1l1lllll1l1_opy_(bstack1l11ll111ll_opy_):
                    continue
                driver = bstack1l1l1l1l1ll_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack1l1ll1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠤ᎘").format(
                        json.dumps(
                            {
                                bstack1l1ll1_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧ᎙"): bstack1l1ll1_opy_ (u"ࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ᎚"),
                                bstack1l1ll1_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ᎛"): {bstack1l1ll1_opy_ (u"ࠣࡰࡤࡱࡪࠨ᎜"): test_name},
                            }
                        )
                    )
                )
            f.bstack1lllllll1ll_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l11l11ll_opy_, True)
    def bstack1l1llll1ll1_opy_(
        self,
        instance: bstack1ll1llllll1_opy_,
        f: TestFramework,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1ll1ll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        bstack1l1ll11111l_opy_ = [d for d, _ in f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1ll11ll11_opy_, [])]
        if not bstack1l1ll11111l_opy_:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡶࡲࠤࡱ࡯࡮࡬ࠤ᎝"))
            return
        if not bstack1l1lll11111_opy_():
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣ᎞"))
            return
        for bstack1l11l1lllll_opy_ in bstack1l1ll11111l_opy_:
            driver = bstack1l11l1lllll_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack1l1ll1_opy_ (u"ࠦࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡗࡾࡴࡣ࠻ࠤ᎟") + str(timestamp)
            driver.execute_script(
                bstack1l1ll1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠥᎠ").format(
                    json.dumps(
                        {
                            bstack1l1ll1_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࠨᎡ"): bstack1l1ll1_opy_ (u"ࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤᎢ"),
                            bstack1l1ll1_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦᎣ"): {
                                bstack1l1ll1_opy_ (u"ࠤࡷࡽࡵ࡫ࠢᎤ"): bstack1l1ll1_opy_ (u"ࠥࡅࡳࡴ࡯ࡵࡣࡷ࡭ࡴࡴࠢᎥ"),
                                bstack1l1ll1_opy_ (u"ࠦࡩࡧࡴࡢࠤᎦ"): data,
                                bstack1l1ll1_opy_ (u"ࠧࡲࡥࡷࡧ࡯ࠦᎧ"): bstack1l1ll1_opy_ (u"ࠨࡤࡦࡤࡸ࡫ࠧᎨ")
                            }
                        }
                    )
                )
            )
    def bstack1l1lll11l1l_opy_(
        self,
        instance: bstack1ll1llllll1_opy_,
        f: TestFramework,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1ll1ll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        keys = [
            bstack1llll1l1ll1_opy_.bstack1l1ll11ll11_opy_,
            bstack1llll1l1ll1_opy_.bstack1l1l111llll_opy_,
        ]
        bstack1l1ll11111l_opy_ = []
        for key in keys:
            bstack1l1ll11111l_opy_.extend(f.bstack111111l111_opy_(instance, key, []))
        if not bstack1l1ll11111l_opy_:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡷࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡫࡯࡮ࡥࠢࡤࡲࡾࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡶࡲࠤࡱ࡯࡮࡬ࠤᎩ"))
            return
        if f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l1ll1ll1_opy_, False):
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡆࡆ࡙ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡤࡴࡨࡥࡹ࡫ࡤࠣᎪ"))
            return
        self.bstack1ll111ll1ll_opy_()
        bstack1l1l1lll1_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack111111l111_opy_(instance, TestFramework.bstack1ll11l1l111_opy_)
        req.test_framework_name = TestFramework.bstack111111l111_opy_(instance, TestFramework.bstack1ll1l11l1ll_opy_)
        req.test_framework_version = TestFramework.bstack111111l111_opy_(instance, TestFramework.bstack1l1ll1ll1l1_opy_)
        req.test_framework_state = bstack1llllll1111_opy_[0].name
        req.test_hook_state = bstack1llllll1111_opy_[1].name
        req.test_uuid = TestFramework.bstack111111l111_opy_(instance, TestFramework.bstack1ll11l1l1ll_opy_)
        for bstack1l1l1l1l1ll_opy_, driver in bstack1l1ll11111l_opy_:
            try:
                webdriver = bstack1l1l1l1l1ll_opy_()
                if webdriver is None:
                    self.logger.debug(bstack1l1ll1_opy_ (u"ࠤ࡚ࡩࡧࡊࡲࡪࡸࡨࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡪࡵࠣࡒࡴࡴࡥࠡࠪࡵࡩ࡫࡫ࡲࡦࡰࡦࡩࠥ࡫ࡸࡱ࡫ࡵࡩࡩ࠯ࠢᎫ"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack1l1ll1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠤᎬ")
                    if bstack1lll1l1l1ll_opy_.bstack111111l111_opy_(driver, bstack1lll1l1l1ll_opy_.bstack1l11ll111l1_opy_, False)
                    else bstack1l1ll1_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࡤ࡭ࡲࡪࡦࠥᎭ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1lll1l1l1ll_opy_.bstack111111l111_opy_(driver, bstack1lll1l1l1ll_opy_.bstack1l1l11ll11l_opy_, bstack1l1ll1_opy_ (u"ࠧࠨᎮ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1lll1l1l1ll_opy_.bstack111111l111_opy_(driver, bstack1lll1l1l1ll_opy_.bstack1l1l11l1ll1_opy_, bstack1l1ll1_opy_ (u"ࠨࠢᎯ"))
                caps = None
                if hasattr(webdriver, bstack1l1ll1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᎰ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack1l1ll1_opy_ (u"ࠣࡕࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࡦࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢࡧ࡭ࡷ࡫ࡣࡵ࡮ࡼࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠰ࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᎱ"))
                    except Exception as e:
                        self.logger.debug(bstack1l1ll1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡨࡵࡳࡲࠦࡤࡳ࡫ࡹࡩࡷ࠴ࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷ࠿ࠦࠢᎲ") + str(e) + bstack1l1ll1_opy_ (u"ࠥࠦᎳ"))
                try:
                    bstack1l11ll11l11_opy_ = json.dumps(caps).encode(bstack1l1ll1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᎴ")) if caps else bstack1l11ll1111l_opy_ (u"ࠧࢁࡽࠣᎵ")
                    req.capabilities = bstack1l11ll11l11_opy_
                except Exception as e:
                    self.logger.debug(bstack1l1ll1_opy_ (u"ࠨࡧࡦࡶࡢࡧࡧࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡴࡤࠡࡵࡨࡶ࡮ࡧ࡬ࡪࡼࡨࠤࡨࡧࡰࡴࠢࡩࡳࡷࠦࡲࡦࡳࡸࡩࡸࡺ࠺ࠡࠤᎶ") + str(e) + bstack1l1ll1_opy_ (u"ࠢࠣᎷ"))
            except Exception as e:
                self.logger.error(bstack1l1ll1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡩࡸࡩࡷࡧࡵࠤ࡮ࡺࡥ࡮࠼ࠣࠦᎸ") + str(str(e)) + bstack1l1ll1_opy_ (u"ࠤࠥᎹ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11l11ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llllll1_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
        *args,
        **kwargs
    ):
        bstack1l1ll11111l_opy_ = f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1ll11ll11_opy_, [])
        if not bstack1l1lll11111_opy_() and len(bstack1l1ll11111l_opy_) == 0:
            bstack1l1ll11111l_opy_ = f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l111llll_opy_, [])
        if not bstack1l1ll11111l_opy_:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᎺ") + str(kwargs) + bstack1l1ll1_opy_ (u"ࠦࠧᎻ"))
            return {}
        if len(bstack1l1ll11111l_opy_) > 1:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠࡼ࡮ࡨࡲ࠭ࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳࠪࡿࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᎼ") + str(kwargs) + bstack1l1ll1_opy_ (u"ࠨࠢᎽ"))
            return {}
        bstack1l1l1l1l1ll_opy_, bstack1l1l1l1ll11_opy_ = bstack1l1ll11111l_opy_[0]
        driver = bstack1l1l1l1l1ll_opy_()
        if not driver:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᎾ") + str(kwargs) + bstack1l1ll1_opy_ (u"ࠣࠤᎿ"))
            return {}
        capabilities = f.bstack111111l111_opy_(bstack1l1l1l1ll11_opy_, bstack1lll1l1l1ll_opy_.bstack1l1l11llll1_opy_)
        if not capabilities:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠦࡦࡰࡷࡱࡨࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᏀ") + str(kwargs) + bstack1l1ll1_opy_ (u"ࠥࠦᏁ"))
            return {}
        return capabilities.get(bstack1l1ll1_opy_ (u"ࠦࡦࡲࡷࡢࡻࡶࡑࡦࡺࡣࡩࠤᏂ"), {})
    def bstack1ll11l1ll1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llllll1_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1ll1llll111_opy_, bstack1ll1lllll1l_opy_],
        *args,
        **kwargs
    ):
        bstack1l1ll11111l_opy_ = f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1ll11ll11_opy_, [])
        if not bstack1l1lll11111_opy_() and len(bstack1l1ll11111l_opy_) == 0:
            bstack1l1ll11111l_opy_ = f.bstack111111l111_opy_(instance, bstack1llll1l1ll1_opy_.bstack1l1l111llll_opy_, [])
        if not bstack1l1ll11111l_opy_:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᏃ") + str(kwargs) + bstack1l1ll1_opy_ (u"ࠨࠢᏄ"))
            return
        if len(bstack1l1ll11111l_opy_) > 1:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡾࡰࡪࡴࠨࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᏅ") + str(kwargs) + bstack1l1ll1_opy_ (u"ࠣࠤᏆ"))
        bstack1l1l1l1l1ll_opy_, bstack1l1l1l1ll11_opy_ = bstack1l1ll11111l_opy_[0]
        driver = bstack1l1l1l1l1ll_opy_()
        if not driver:
            self.logger.debug(bstack1l1ll1_opy_ (u"ࠤࡪࡩࡹࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡨࡷ࡯ࡶࡦࡴ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᏇ") + str(kwargs) + bstack1l1ll1_opy_ (u"ࠥࠦᏈ"))
            return
        return driver