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
import os
import json
import shutil
import tempfile
import threading
import urllib.request
import uuid
from pathlib import Path
import logging
import re
from bstack_utils.helper import bstack1l1l1lll11l_opy_
bstack11lll1l1ll1_opy_ = 100 * 1024 * 1024 # 100 bstack11lll1l111l_opy_
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
bstack1l1l1llllll_opy_ = bstack1l1l1lll11l_opy_()
bstack1l1lll1ll1l_opy_ = bstack1l1ll1_opy_ (u"ࠢࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠳ࠢᖨ")
bstack11llllll11l_opy_ = bstack1l1ll1_opy_ (u"ࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦᖩ")
bstack11lllll1lll_opy_ = bstack1l1ll1_opy_ (u"ࠤࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠨᖪ")
bstack11llllll1l1_opy_ = bstack1l1ll1_opy_ (u"ࠥࡌࡴࡵ࡫ࡍࡧࡹࡩࡱࠨᖫ")
bstack11lll1lllll_opy_ = bstack1l1ll1_opy_ (u"ࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠥᖬ")
_11lll1ll11l_opy_ = threading.local()
def bstack1l111lllll1_opy_(test_framework_state, test_hook_state):
    bstack1l1ll1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤ࡙ࠥࡥࡵࠢࡷ࡬ࡪࠦࡣࡶࡴࡵࡩࡳࡺࠠࡵࡧࡶࡸࠥ࡫ࡶࡦࡰࡷࠤࡸࡺࡡࡵࡧࠣ࡭ࡳࠦࡴࡩࡴࡨࡥࡩ࠳࡬ࡰࡥࡤࡰࠥࡹࡴࡰࡴࡤ࡫ࡪ࠴ࠊࠡࠢࠣࠤ࡙࡮ࡩࡴࠢࡩࡹࡳࡩࡴࡪࡱࡱࠤࡸ࡮࡯ࡶ࡮ࡧࠤࡧ࡫ࠠࡤࡣ࡯ࡰࡪࡪࠠࡣࡻࠣࡸ࡭࡫ࠠࡦࡸࡨࡲࡹࠦࡨࡢࡰࡧࡰࡪࡸࠠࠩࡵࡸࡧ࡭ࠦࡡࡴࠢࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺࠩࠋࠢࠣࠤࠥࡨࡥࡧࡱࡵࡩࠥࡧ࡮ࡺࠢࡩ࡭ࡱ࡫ࠠࡶࡲ࡯ࡳࡦࡪࡳࠡࡱࡦࡧࡺࡸ࠮ࠋࠢࠣࠤࠥࠨࠢࠣᖭ")
    _11lll1ll11l_opy_.test_framework_state = test_framework_state
    _11lll1ll11l_opy_.test_hook_state = test_hook_state
def bstack11lll1ll111_opy_():
    bstack1l1ll1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡒࡦࡶࡵ࡭ࡪࡼࡥࠡࡶ࡫ࡩࠥࡩࡵࡳࡴࡨࡲࡹࠦࡴࡦࡵࡷࠤࡪࡼࡥ࡯ࡶࠣࡷࡹࡧࡴࡦࠢࡩࡶࡴࡳࠠࡵࡪࡵࡩࡦࡪ࠭࡭ࡱࡦࡥࡱࠦࡳࡵࡱࡵࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࠦࡡࠡࡶࡸࡴࡱ࡫ࠠࠩࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥ࠭ࠢࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨ࠭ࠥࡵࡲࠡࠪࡑࡳࡳ࡫ࠬࠡࡐࡲࡲࡪ࠯ࠠࡪࡨࠣࡲࡴࡺࠠࡴࡧࡷ࠲ࠏࠦࠠࠡࠢࠥࠦࠧᖮ")
    return (
        getattr(_11lll1ll11l_opy_, bstack1l1ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࠧᖯ"), None),
        getattr(_11lll1ll11l_opy_, bstack1l1ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࠪᖰ"), None)
    )
class bstack1l1ll11l11_opy_:
    bstack1l1ll1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡉ࡭ࡱ࡫ࡕࡱ࡮ࡲࡥࡩ࡫ࡲࠡࡲࡵࡳࡻ࡯ࡤࡦࡵࠣࡪࡺࡴࡣࡵ࡫ࡲࡲࡦࡲࡩࡵࡻࠣࡸࡴࠦࡵࡱ࡮ࡲࡥࡩࠦࡡ࡯ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡢࡢࡵࡨࡨࠥࡵ࡮ࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤ࡫࡯࡬ࡦࠢࡳࡥࡹ࡮࠮ࠋࠢࠣࠤࠥࡏࡴࠡࡵࡸࡴࡵࡵࡲࡵࡵࠣࡦࡴࡺࡨࠡ࡮ࡲࡧࡦࡲࠠࡧ࡫࡯ࡩࠥࡶࡡࡵࡪࡶࠤࡦࡴࡤࠡࡊࡗࡘࡕ࠵ࡈࡕࡖࡓࡗ࡛ࠥࡒࡍࡵ࠯ࠤࡦࡴࡤࠡࡥࡲࡴ࡮࡫ࡳࠡࡶ࡫ࡩࠥ࡬ࡩ࡭ࡧࠣ࡭ࡳࡺ࡯ࠡࡣࠣࡨࡪࡹࡩࡨࡰࡤࡸࡪࡪࠊࠡࠢࠣࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠࡸ࡫ࡷ࡬࡮ࡴࠠࡵࡪࡨࠤࡺࡹࡥࡳࠩࡶࠤ࡭ࡵ࡭ࡦࠢࡩࡳࡱࡪࡥࡳࠢࡸࡲࡩ࡫ࡲࠡࢀ࠲࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠲࡙ࡵࡲ࡯ࡢࡦࡨࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴ࠰ࠍࠤࠥࠦࠠࡊࡨࠣࡥࡳࠦ࡯ࡱࡶ࡬ࡳࡳࡧ࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥࡶࡡࡳࡣࡰࡩࡹ࡫ࡲࠡࠪ࡬ࡲࠥࡐࡓࡐࡐࠣࡪࡴࡸ࡭ࡢࡶࠬࠤ࡮ࡹࠠࡱࡴࡲࡺ࡮ࡪࡥࡥࠢࡤࡲࡩࠦࡣࡰࡰࡷࡥ࡮ࡴࡳࠡࡣࠣࡸࡷࡻࡴࡩࡻࠣࡺࡦࡲࡵࡦࠌࠣࠤࠥࠦࡦࡰࡴࠣࡸ࡭࡫ࠠ࡬ࡧࡼࠤࠧࡨࡵࡪ࡮ࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࠢ࠭ࠢࡷ࡬ࡪࠦࡦࡪ࡮ࡨࠤࡼ࡯࡬࡭ࠢࡥࡩࠥࡶ࡬ࡢࡥࡨࡨࠥ࡯࡮ࠡࡶ࡫ࡩࠥࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥࠤ࡫ࡵ࡬ࡥࡧࡵ࠿ࠥࡵࡴࡩࡧࡵࡻ࡮ࡹࡥ࠭ࠌࠣࠤࠥࠦࡩࡵࠢࡧࡩ࡫ࡧࡵ࡭ࡶࡶࠤࡹࡵࠠࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦ࠳ࠐࠠࠡࠢࠣࡘ࡭࡯ࡳࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡲࡪࠥࡧࡤࡥࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡩࡴࠢࡤࠤࡻࡵࡩࡥࠢࡰࡩࡹ࡮࡯ࡥ⠖࡬ࡸࠥ࡮ࡡ࡯ࡦ࡯ࡩࡸࠦࡡ࡭࡮ࠣࡩࡷࡸ࡯ࡳࡵࠣ࡫ࡷࡧࡣࡦࡨࡸࡰࡱࡿࠠࡣࡻࠣࡰࡴ࡭ࡧࡪࡰࡪࠎࠥࠦࠠࠡࡶ࡫ࡩࡲࠦࡡ࡯ࡦࠣࡷ࡮ࡳࡰ࡭ࡻࠣࡶࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡷࡪࡶ࡫ࡳࡺࡺࠠࡵࡪࡵࡳࡼ࡯࡮ࡨࠢࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࡸ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᖱ")
    @staticmethod
    def upload_attachment(bstack11lll1l1111_opy_: str, *bstack11lll1lll11_opy_) -> None:
        if not bstack11lll1l1111_opy_ or not bstack11lll1l1111_opy_.strip():
            logger.error(bstack1l1ll1_opy_ (u"ࠥࡥࡩࡪ࡟ࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤ࡫ࡧࡩ࡭ࡧࡧ࠾ࠥࡖࡲࡰࡸ࡬ࡨࡪࡪࠠࡧ࡫࡯ࡩࠥࡶࡡࡵࡪࠣ࡭ࡸࠦࡥ࡮ࡲࡷࡽࠥࡵࡲࠡࡐࡲࡲࡪ࠴ࠢᖲ"))
            return
        bstack11lll11llll_opy_ = bstack11lll1lll11_opy_[0] if bstack11lll1lll11_opy_ and len(bstack11lll1lll11_opy_) > 0 else None
        bstack11lll1l1l1l_opy_ = None
        test_framework_state, test_hook_state = bstack11lll1ll111_opy_()
        try:
            if bstack11lll1l1111_opy_.startswith(bstack1l1ll1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧᖳ")) or bstack11lll1l1111_opy_.startswith(bstack1l1ll1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢᖴ")):
                logger.debug(bstack1l1ll1_opy_ (u"ࠨࡐࡢࡶ࡫ࠤ࡮ࡹࠠࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡧࠤࡦࡹࠠࡖࡔࡏ࠿ࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࡩ࡯ࡩࠣࡸ࡭࡫ࠠࡧ࡫࡯ࡩ࠳ࠨᖵ"))
                url = bstack11lll1l1111_opy_
                bstack11lll1lll1l_opy_ = str(uuid.uuid4())
                bstack11lll1l1lll_opy_ = os.path.basename(urllib.request.urlparse(url).path)
                if not bstack11lll1l1lll_opy_ or not bstack11lll1l1lll_opy_.strip():
                    bstack11lll1l1lll_opy_ = bstack11lll1lll1l_opy_
                temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                        prefix=bstack1l1ll1_opy_ (u"ࠢࡶࡲ࡯ࡳࡦࡪ࡟ࠣᖶ") + bstack11lll1lll1l_opy_ + bstack1l1ll1_opy_ (u"ࠣࡡࠥᖷ"),
                                                        suffix=bstack1l1ll1_opy_ (u"ࠤࡢࠦᖸ") + bstack11lll1l1lll_opy_)
                with urllib.request.urlopen(url) as response, open(temp_file.name, bstack1l1ll1_opy_ (u"ࠪࡻࡧ࠭ᖹ")) as out_file:
                    shutil.copyfileobj(response, out_file)
                bstack11lll1l1l1l_opy_ = Path(temp_file.name)
                logger.debug(bstack1l1ll1_opy_ (u"ࠦࡉࡵࡷ࡯࡮ࡲࡥࡩ࡫ࡤࠡࡨ࡬ࡰࡪࠦࡴࡰࠢࡷࡩࡲࡶ࡯ࡳࡣࡵࡽࠥࡲ࡯ࡤࡣࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦᖺ").format(bstack11lll1l1l1l_opy_))
            else:
                bstack11lll1l1l1l_opy_ = Path(bstack11lll1l1111_opy_)
                logger.debug(bstack1l1ll1_opy_ (u"ࠧࡖࡡࡵࡪࠣ࡭ࡸࠦࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡦࠣࡥࡸࠦ࡬ࡰࡥࡤࡰࠥ࡬ࡩ࡭ࡧ࠽ࠤࢀࢃࠢᖻ").format(bstack11lll1l1l1l_opy_))
        except Exception as e:
            logger.error(bstack1l1ll1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡲࡦࡹࡧࡩ࡯ࠢࡩ࡭ࡱ࡫ࠠࡧࡴࡲࡱࠥࡶࡡࡵࡪ࠲࡙ࡗࡒ࠺ࠡࡽࢀࠦᖼ").format(e))
            return
        if bstack11lll1l1l1l_opy_ is None or not bstack11lll1l1l1l_opy_.exists():
            logger.error(bstack1l1ll1_opy_ (u"ࠢࡔࡱࡸࡶࡨ࡫ࠠࡧ࡫࡯ࡩࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡦࡺ࡬ࡷࡹࡀࠠࡼࡿࠥᖽ").format(bstack11lll1l1l1l_opy_))
            return
        if bstack11lll1l1l1l_opy_.stat().st_size > bstack11lll1l1ll1_opy_:
            logger.error(bstack1l1ll1_opy_ (u"ࠣࡈ࡬ࡰࡪࠦࡳࡪࡼࡨࠤࡪࡾࡣࡦࡧࡧࡷࠥࡳࡡࡹ࡫ࡰࡹࡲࠦࡡ࡭࡮ࡲࡻࡪࡪࠠࡴ࡫ࡽࡩࠥࡵࡦࠡࡽࢀࠦᖾ").format(bstack11lll1l1ll1_opy_))
            return
        bstack11lll1llll1_opy_ = bstack1l1ll1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᖿ")
        if bstack11lll11llll_opy_:
            try:
                params = json.loads(bstack11lll11llll_opy_)
                if bstack1l1ll1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠧᗀ") in params and params.get(bstack1l1ll1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨᗁ")) is True:
                    bstack11lll1llll1_opy_ = bstack1l1ll1_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤᗂ")
            except Exception as bstack11lll1l11l1_opy_:
                logger.error(bstack1l1ll1_opy_ (u"ࠨࡊࡔࡑࡑࠤࡵࡧࡲࡴ࡫ࡱ࡫ࠥ࡫ࡲࡳࡱࡵࠤ࡮ࡴࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡔࡦࡸࡡ࡮ࡵ࠽ࠤࢀࢃࠢᗃ").format(bstack11lll1l11l1_opy_))
        bstack11lll1l11ll_opy_ = False
        from browserstack_sdk.sdk_cli.bstack1lll1ll1111_opy_ import bstack1lll1l1lll1_opy_
        if test_framework_state in bstack1lll1l1lll1_opy_.bstack11lllllll1l_opy_:
            if bstack11lll1llll1_opy_ == bstack11lllll1lll_opy_:
                bstack11lll1l11ll_opy_ = True
            bstack11lll1llll1_opy_ = bstack11llllll1l1_opy_
        try:
            platform_index = os.environ[bstack1l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧᗄ")]
            target_dir = os.path.join(bstack1l1l1llllll_opy_, bstack1l1lll1ll1l_opy_ + str(platform_index),
                                      bstack11lll1llll1_opy_)
            if bstack11lll1l11ll_opy_:
                target_dir = os.path.join(target_dir, bstack11lll1lllll_opy_)
            os.makedirs(target_dir, exist_ok=True)
            logger.debug(bstack1l1ll1_opy_ (u"ࠣࡅࡵࡩࡦࡺࡥࡥ࠱ࡹࡩࡷ࡯ࡦࡪࡧࡧࠤࡹࡧࡲࡨࡧࡷࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠺ࠡࡽࢀࠦᗅ").format(target_dir))
            file_name = os.path.basename(bstack11lll1l1l1l_opy_)
            bstack11lll1ll1ll_opy_ = os.path.join(target_dir, file_name)
            if os.path.exists(bstack11lll1ll1ll_opy_):
                base_name, extension = os.path.splitext(file_name)
                bstack11llll11111_opy_ = 1
                while os.path.exists(os.path.join(target_dir, base_name + str(bstack11llll11111_opy_) + extension)):
                    bstack11llll11111_opy_ += 1
                bstack11lll1ll1ll_opy_ = os.path.join(target_dir, base_name + str(bstack11llll11111_opy_) + extension)
            shutil.copy(bstack11lll1l1l1l_opy_, bstack11lll1ll1ll_opy_)
            logger.info(bstack1l1ll1_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡣࡰࡲ࡬ࡩࡩࠦࡴࡰ࠼ࠣࡿࢂࠨᗆ").format(bstack11lll1ll1ll_opy_))
        except Exception as e:
            logger.error(bstack1l1ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡰࡳࡻ࡯࡮ࡨࠢࡩ࡭ࡱ࡫ࠠࡵࡱࠣࡸࡦࡸࡧࡦࡶࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࡀࠠࡼࡿࠥᗇ").format(e))
            return
        finally:
            if bstack11lll1l1111_opy_.startswith(bstack1l1ll1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧᗈ")) or bstack11lll1l1111_opy_.startswith(bstack1l1ll1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࠢᗉ")):
                try:
                    if bstack11lll1l1l1l_opy_ is not None and bstack11lll1l1l1l_opy_.exists():
                        bstack11lll1l1l1l_opy_.unlink()
                        logger.debug(bstack1l1ll1_opy_ (u"ࠨࡔࡦ࡯ࡳࡳࡷࡧࡲࡺࠢࡩ࡭ࡱ࡫ࠠࡥࡧ࡯ࡩࡹ࡫ࡤ࠻ࠢࡾࢁࠧᗊ").format(bstack11lll1l1l1l_opy_))
                except Exception as ex:
                    logger.error(bstack1l1ll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡤࡦ࡮ࡨࡸ࡮ࡴࡧࠡࡶࡨࡱࡵࡵࡲࡢࡴࡼࠤ࡫࡯࡬ࡦ࠼ࠣࡿࢂࠨᗋ").format(ex))
    @staticmethod
    def bstack1l1ll111_opy_() -> None:
        bstack1l1ll1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡊࡥ࡭ࡧࡷࡩࡸࠦࡡ࡭࡮ࠣࡪࡴࡲࡤࡦࡴࡶࠤࡼ࡮࡯ࡴࡧࠣࡲࡦࡳࡥࡴࠢࡶࡸࡦࡸࡴࠡࡹ࡬ࡸ࡭ࠦࠢࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠳ࠢࠡࡨࡲࡰࡱࡵࡷࡦࡦࠣࡦࡾࠦࡡࠡࡰࡸࡱࡧ࡫ࡲࠡ࡫ࡱࠎࠥࠦࠠࠡࠢࠣࠤࠥࡺࡨࡦࠢࡸࡷࡪࡸࠧࡴࠢࢁ࠳࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧᗌ")
        bstack11lll1l1l11_opy_ = bstack1l1l1lll11l_opy_()
        pattern = re.compile(bstack1l1ll1_opy_ (u"ࡴ࡙ࠥࡵࡲ࡯ࡢࡦࡨࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴ࠯࡟ࡨ࠰ࠨᗍ"))
        if os.path.exists(bstack11lll1l1l11_opy_):
            for item in os.listdir(bstack11lll1l1l11_opy_):
                bstack11lll1ll1l1_opy_ = os.path.join(bstack11lll1l1l11_opy_, item)
                if os.path.isdir(bstack11lll1ll1l1_opy_) and pattern.fullmatch(item):
                    try:
                        shutil.rmtree(bstack11lll1ll1l1_opy_)
                    except Exception as e:
                        logger.error(bstack1l1ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡧࡩࡱ࡫ࡴࡪࡰࡪࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠺ࠡࡽࢀࠦᗎ").format(e))
        else:
            logger.info(bstack1l1ll1_opy_ (u"࡙ࠦ࡮ࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠤᗏ").format(bstack11lll1l1l11_opy_))