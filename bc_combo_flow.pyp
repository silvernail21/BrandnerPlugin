# TODO(Andreas): Have warning for multiple objects with identical names?
# TODO(Andreas): Check resulting doc name (appended date) with Brandner.
#                Naming convention?
#                Need configurable?
# TODO(Andreas): If I had written this from scratch, I likely would have stored
#                object links instead of just keeping names and always
#                searching for objects.
#                Yet, this is not a five minute change.

import logging

import c4d

# A funky bit of code...
#
# Just ignore and don't touch, please.
# Source: Niklas Rosenstein
# Personally known as very capable, thorough and
# trustworthy developer.
#
# Throws flake8 warnings (flake/PEP8 doesn't like dense code).
# Ignore the warnings.
# Not sure how to disable the warnings. :(
# At least not without modifying and breaking its compactness.
#
# Open source, snippet was generated (minified) from:
# https://github.com/NiklasRosenstein/python-localimport
# Snippet simply copy/pasted from here
# (the two versions there only differ in maximum codeline width):
# https://gist.github.com/NiklasRosenstein/f5690d8f36bbdc8e5556#file-localimport-blob-mcw99-py
# Explanation:
# https://developers.maxon.net/forum/topic/7016/7915_external-dependencies-the-right-way-to-do
# The long story, that lead to this solution:
# https://developers.maxon.net/forum/topic/8229/10727_best-practice-for-imports
# BEGIN PASTE localimport
# localimport-v1.7.3-blob-mcw99
import base64 as b, types as t, zlib as z; m=t.ModuleType('localimport');
m.__file__ = __file__; blob=b'\
eJydWUuP20YSvutXEMiBpIfmeOLDAkJo7GaRAMEGORiLPUQrEBTVkumhSKK75Uhj5L+nHv2iSNpyfBiTXY+uqq76qpoqy+qsP\
/SyLIv4t+a5rVT0vleiU1o0XfSDdM8dEf95PFVNm9f96V28KstPQqqm71D4Kf9H/jZeNaehlzqq++Fqn49tv7PPvbJPw/PxrJ\
vWvqqro2hZ1WJX1c924aUZDk0rVs0B2XK7adMd+s2bbVF8v15Fe3GIGi1OKrmk8BpJoc+yiy45L6aOQy5xScspWiWWNbaN0ol\
Te4de0klMqmz7umoTdKarTiIbKv0B9aGMXSx6leN6Xu0U/u+4YatDLyNcK/E9gvOxCnBPR5hocBRQETVkiDrvRsozz4O6rAP/\
lWexsi8/VxAY64lVgH9AWIqOvNDyyv63SHCWmPcR9yoSl1oMOvpf1Z7FT1L2MggdbRa5va1C1Fif5b6REcSi67Wl5EpXUqs/G\
tiFdkUejrv4VLXlEDqr4FiAnO2F0sVvfScyzjRFL+gHRAmJ4GmES2gYMWP+4XbEgdtbDxuF2v1heVdWERoV9YPovAWxjFMotc\
OAfHisTbcXl6xtOjpX0Z1PQlYaFA58ILAdEkM3YzY6ZgY6WPYitBr+iYuo0f+Syd4I2vPhiXZNidekPqljXXk1gOH7ZEGKxLw\
U0Qoy9ADPSfxdnDrjkPbuzRqpxLJZ09KWGNwqeCibIXFi4yBDSie0sbGSxCz5Y990iX2B80Vz/YkEbo6kul6eKDk93QQ7qro9\
P6ARcCyYAmZjfMybTgkI6Bur2iQr0jjzliKP/F2fWU/Invj/XfwqYcrrp/RhHAxTWKgxAfQdMNmQI/MphbQ49XX1Y6XET/QIa\
InCDljzQTadLoHPQJO4aDjkkmsUStSmMNIAfUuT3S+OEOFDLtm8+JFO2XhvseklxyeCS6AOI2Sik3pFOtTQNjqJc7L8hbhAH3\
NMGZqu0eVwLeKypMcyfgCdYL4Sw0M8XGPHUi/y1J6pX2TqgenUc0gKcgLiEkAwemjBYM2watoUZGlpHgnvOFXN+cEJHo+F5fy\
9GX62bAQJxFHt97RrEkQepDIKzkP8aC3Owd0UzPk6W30nXx9zQQMuhehNZ2GgG/682FZCXhtrqVZIzBaLjZ4pGPtqAYV4GT4o\
RxMblB+r/e/8mNmlXyt5FCZYpvKHSqloFWDPksXOWLDV4wigAx8Omr1stTuKG5if7mMSKsVA38tcfxN3n6azQf+GmJuQc6FuJ\
gB4STG7L6Gi7apuMdI0uBgU63cfRU3dHqx6+1zMzGTvirdARXTojqW+DkIVCbxlKdhOQnRuyQ4QipkyM0jZZEyUaA9ZMC6UcG\
Lcqvd9CemrCpxN8AXq0j3DLNvvsUu0gtZSU5oYHq+HonOQCDVoe3kUmt6SpzQ/lDiuwvBhUgbwAY8F8AHDQmw2AZ1Zty1nMsG\
h1MZr2tJBoofEV2y2di6DhqKrrjaIQByjKKY+1Td8PNH8UGhnhmn3vBn0FqIDaF41MID52SyJYdKqdPNJcMbtzhoEAzmDXtMx\
1GSy5QtGzdUsv8vHMaOLV5jNZVjeJjPYAc/OzS3Bc83xz7TESm6gr3IQj1N/Oiehq9IfEa/1+3ML+fz5T7ticpD/s4tNV9Z9p\
2Hvgudmzxwm6fjVZYUbGZRLjmCrNYdDdIUSmielSRI49zkaSD90SLgnDLAHhMEOggcjiTuu0ammw1tBZIzIAYySQ5eaYdMN25\
0/aB60nUlu2r511oEApIqQBgVSHl24ffrLYymF6s+yFlSpHSB6rQu8duZ7IQZ8SEZcOVkCBVkLONL6uToKRTbvBUCcFJ5cjOU\
mdMraL7OwZ+WcqBnOfiFH3K3HOoAIN2+UoZBiAAktis8xC8Vr/j+LJ1LxerKUgRQegorXn//MYnyM13aS2ay3WeyyntfdKxFN\
plppvsTnwfwYr2cWMyoWv4nPBbMeblKMa+9hRF9F0Yz+Ing2kPgsrhnUKiYuX8LD6vUzmY/nxvu23YD0lpqDEciHfkhgMRhYo\
v+IK58fziJUkp6fFcDLytaenfmVPmlfoD7316u5q9pILA2C+FCEllPgt4uee7vcZZIYwmviIMWhuRQgnEsAa93grYHGbujntl\
N8qFSltQw15tA9ExZOM+hxVPSlvZRCIreTuPCdMVAHxKlo6J9NWXMwVOZU4iCZW0FGoHClmEmVkUjGL1gcLH+L3fwBJMTfAK7\
Xri0Fi0lwFUKag7SLn2tewWbBZHKzKX+Aofb7/gxoe7IN2NBJhhBS7Knp0nBGHpl2sXRJwQ3DcXGaQhz6QOHN6DhWPeoxN7oD\
HXcpxQq39rpqd9lKROWiRYMvLc544vFr60acCe94i9t+bw3EBTTQNv0w7yn/0tmaM98CRzUHXNh5+sHNA/6TH5RQWAdmTMzoY\
1QwyFl+8h52dA6BVbtz00JjLnlPhvtwUOXCdnfp7Cksa2Yxcz+abIIyZyBVMQtsZ40NPyJ5p00h0TRhFyNI6pFP0y+kQdKkIS\
6MYHYBp8Pl87DHr2nzaP/FQ1wQcQ3EDLYUJoyx/1yxef39NmgXv+DHLtswvIzt+O4YSheO8N1WRng+5mRDeA1EtiZafHJMyG4\
tfNqix2EAbHHPR8ABcdBBb9A9QF/uxkv9cjIP3Daz+cFgWuULM8FI58ygsr1jrrxrzrPZMZm+tlMVM1NoXreikjzHf515JpPN\
GEh5PDNe2nAvXEuoQzttpl1NfLEXcrLC3x+/4n8yEmAgvclXT9+uvrV732hHy6FE6/6TkP7qYHqxVYZ5bVDSpLbpQkaaejg5y\
0xhow4u6ExcvKJveFww6sYfVkCOEsP+PBCp86404xeTH6A4g65DV81lgJqZ7oCxMLoilgt/OPD7GUi9xTHYnm+FN3CxBrwwGH\
8XpkWn6TT8t5DuLqjz31gpqb8Me/a6yn78C3ib3Vn7n6F4Uyqc+/r70qD7pQsGRQTzLpwfXeLivm1f7YXM+IcXBTnsBhiX6Kk\
fQ60Krofvon9LAfvuo901Gq6npmsOjZBR8kHrQa0fH4+QDOcd/pj7CNO47g+HR8+WrlZ/AaI7XVw='
exec(z.decompress(b.b64decode(blob)), vars(m)); _localimport=m;localimport=getattr(m,"localimport")
del blob, b, t, z, m;
# END PASTE localimport
# ... end of funk.

# Above snippet provides us with localimport, allowing us to do the following.
# No more worries about local modules and reloading plugins, anymore.
# Thanks, Niklas!
with localimport(".") as _importer:
    from bccf_constants import (  # noqa: E402
        PLUGIN_ID_BRANDNER,
        PLUGIN_NAME_BRANDNER,
        PLUGIN_TOOLTIP_BRANDNER)
    from bccf_dialog import BrandnerDialog  # noqa: E402
    from bccf_render_tokens import get_tokens_list  # noqa: E402


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


g_dialog: c4d.gui.GeDialog = None


class CommandDataBrandner(c4d.plugins.CommandData):
    dialog: c4d.gui.GeDialog = None

    def Execute(self, doc):
        global g_dialog

        if self.dialog is None:
            self.dialog = BrandnerDialog()
        g_dialog = self.dialog

        is_open = self.dialog.Open(
            dlgtype=c4d.DLG_TYPE_ASYNC,
            pluginid=PLUGIN_ID_BRANDNER,
            defaultw=400, defaulth=200)
        if is_open:
            self.dialog.layout_changed_components()
        return is_open

    def RestoreLayout(self, sec_ref):
        """Called during C4D startup when the dialog is part of the saved
        layout. C4D is NOT fully initialized yet — keep this path minimal
        and never let it raise, or startup wedges at the splash screen.
        """
        global g_dialog

        try:
            if self.dialog is None:
                self.dialog = BrandnerDialog()
            g_dialog = self.dialog

            # Tell InitValues to skip heavy work (scene clone, document
            # walks) during startup; the first EVMSG_CHANGE afterwards
            # triggers a full refresh.
            self.dialog._is_layout_restore = True

            return self.dialog.Restore(
                pluginid=PLUGIN_ID_BRANDNER, secret=sec_ref)
        except Exception as err:
            logging.error("BC-ComboFlow: RestoreLayout failed: %s", err)
            return True


def plugin_message_end_activity(id: int, data: c4d.BaseContainer) -> bool:
    """Handles plugin messages of types C4DPL_ENDACTIVITY,
    C4DPL_SHUTDOWNTHREADS and C4DPL_RELOADPYTHONPLUGINS.
    """

    global g_dialog

    if g_dialog is not None:
        if g_dialog.IsOpen():
            g_dialog.Close()
        g_dialog = None
    return True


def PluginMessage(id, data):
    """C4D function

    Called in certain stages of C4D's startup/shutdown process.
    """

    if id in [c4d.C4DPL_ENDACTIVITY,
              c4d.C4DPL_SHUTDOWNTHREADS,
              c4d.C4DPL_RELOADPYTHONPLUGINS]:
        return plugin_message_end_activity(id, data)

    return False


def register_render_tokens() -> None:
    tokens_to_register = get_tokens_list()
    for _key, _tuple_token in tokens_to_register.items():
        result = c4d.plugins.RegisterToken(
            key=_key,
            help=_tuple_token[1],
            example=_tuple_token[2],
            hook=_tuple_token[0])
        if not result:
            logging.error(f"FAILED to register token: {_key} ({result})")
        else:
            logging.info(f"Registered token: {_key} ({result})")


def register_command_data() -> None:
    if not c4d.plugins.RegisterCommandPlugin(
            id=PLUGIN_ID_BRANDNER,
            str=PLUGIN_NAME_BRANDNER,
            help=PLUGIN_TOOLTIP_BRANDNER,
            info=0,
            dat=CommandDataBrandner(),
            icon=pluginIcon):
        logging.error(f"{PLUGIN_NAME_BRANDNER} registration failed.")


if __name__ == "__main__":
    pluginIcon = c4d.bitmaps.BaseBitmap()

    register_render_tokens()
    register_command_data()
