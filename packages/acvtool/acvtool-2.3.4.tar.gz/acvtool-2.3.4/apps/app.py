import os

class App(object):
    '''Abastract App class to define paths'''


    def __init__(self):
        self.package = ""
        self.app_dir = ""
        self.base_apk = ""
        self.en_apk = ""
        self.lib_apk = ""
        self.res_apk = ""
        self.apks = []
        self._make_abs_paths()
        

    def _make_abs_paths(self):
        self.base_apk = self._join_dir_path(self.base_apk)
        self.en_apk = self._join_dir_path(self.en_apk)
        self.lib_apk = self._join_dir_path(self.lib_apk)
        self.res_apk = self._join_dir_path(self.res_apk)

    def _join_dir_path(self, fname):
        if fname:
            return os.path.join(self.app_dir, fname)
        return ""

    def __repr__(self):
        return "{}: {}\n{}\n{}\n{}\n{}".format(
            self.package,
            self.app_dir,
            self.base_apk,
            self.en_apk,
            self.lib_apk,
            self.res_apk)


class Twitter(App):
    def __init__(self):
        self.package = "com.twitter.android"
        self.app_dir = "/Users/ap/projects/dblt/googleplay/cmd/googleplay/twitter/"
        self.base_apk = "base.apk"
        self.en_apk = "en-s.apk"
        self.lib_apk = "armeabi-s.apk"
        self.res_apk = "xxhdpi-s.apk"
        App._make_abs_paths()


class MyFitnessPal(App):
    '''All files 24-07-2022:
        base.apk
        split_config.arm64_v8a.apk
        split_config.en.apk
        split_config.ru.apk
        split_config.xxhdpi.apk
        split_nutrition_insights.apk
        split_nutrition_insights.config.xxhdpi.apk
        split_plans.apk
        split_plans.config.xxhdpi.apk
        split_recipe_collection.apk
        split_recipe_collection.config.xxhdpi.apk
    '''
    def __init__(self):
        App.__init__(self)
        self.package = "com.myfitnesspal.android"
        self.app_dir = "/Users/ap/apks/mfp"
        self.apks = get_apks(self.app_dir)
        self.base_apk = next(x for x in self.apks if x.endswith("base.apk"))
        self.supportive_apks = [a for a in self.apks if a != self.base_apk]


def get_apks(dpath):
    apks = [os.path.join(dpath, f) for f in os.listdir(dpath) if f.endswith(".apk")]
    return apks


class DebloatApp(App):
    '''
    Not shrunk version.
    Only webview + firebase dependency + GSM Gradle plugin.
    Only notifications work.
    '''
    def __init__(self):
        super(DebloatApp, self).__init__()
        self.package = "app.debloat"
        # self.app_dir = "/Users/ap/apks/debloatapp/"
        # self.base_apk = "1.1-reb4.apk"
        self.app_dir = "/Users/ap/projects/dblt/apks/debloatapp/"
        self.base_apk = "short-r8.apk"
        self._make_abs_paths()
        self.apks = [self.base_apk]
        self.supportive_apks = []


class Booking(App):
    '''
    The original booking app.
    '''
    def __init__(self):
        super(Booking, self).__init__()
        self.package = "com.booking"
        self.app_dir = "/Users/ap/projects/dblt/apks/booking/"
        self.base_apk = self.app_dir + "base.apk"
        self.supportive_apks = [self.app_dir+a for a in ["split_config.arm64_v8a.apk", "split_config.xxhdpi.apk"]]

class FireAuth(App):
    def __init__(self):
        super(FireAuth, self).__init__()
        self.package = "app.debloat.fireauth"
        self.app_dir = "/Users/ap/projects/dblt/apks/fireauth/"
        self.base_apk = self.app_dir + "FireAuth.apk"
        self.supportive_apks = []


class CurrentApp(FireAuth):
    def __init__(self):
        super(CurrentApp, self).__init__()
