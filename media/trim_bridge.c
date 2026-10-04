/* SPDX-License-Identifier: GPL-3.0-or-later */
/* Local gThumb 3.12 extension: hand the current video to Video Trimmer. */
#include <gtk/gtk.h>
#include <gio/gdesktopappinfo.h>
#include <gmodule.h>
#include <gth-browser.h>
#include <gth-file-data.h>
#include <gth-hook.h>

static gboolean is_video(GthBrowser *browser) {
    GthFileData *file = gth_browser_get_current_file(browser);
    if (!file) return FALSE;
    const char *mime = gth_file_data_get_mime_type(file);
    return mime && g_str_has_prefix(mime, "video/");
}

static void trim_video(GSimpleAction *action, GVariant *parameter, gpointer user_data) {
    GthBrowser *browser = GTH_BROWSER(user_data);
    if (!is_video(browser)) return;
    GthFileData *file = gth_browser_get_current_file(browser);
    GDesktopAppInfo *app = g_desktop_app_info_new("org.gnome.gitlab.YaLTeR.VideoTrimmer.desktop");
    GError *error = NULL;
    gboolean launched = FALSE;
    if (app) {
        char *uri = g_file_get_uri(file->file);
        GList *uris = g_list_append(NULL, uri);
        GdkAppLaunchContext *context = gdk_display_get_app_launch_context(gtk_widget_get_display(GTK_WIDGET(browser)));
        g_app_launch_context_setenv(G_APP_LAUNCH_CONTEXT(context), "GDK_BACKEND", "wayland");
        launched = g_app_info_launch_uris(G_APP_INFO(app), uris, G_APP_LAUNCH_CONTEXT(context), &error);
        g_object_unref(context);
        g_list_free(uris);
        g_free(uri);
        g_object_unref(app);
    }
    if (launched) {
        /* Close only the sending window. Other gThumb windows are unaffected. */
        gtk_window_close(GTK_WINDOW(browser));
    } else {
        GtkWidget *dialog = gtk_message_dialog_new(GTK_WINDOW(browser), GTK_DIALOG_DESTROY_WITH_PARENT,
            GTK_MESSAGE_ERROR, GTK_BUTTONS_CLOSE, "Could not open Video Trimmer");
        gtk_message_dialog_format_secondary_text(GTK_MESSAGE_DIALOG(dialog), "%s",
            error ? error->message : "Video Trimmer is not installed.");
        g_signal_connect_swapped(dialog, "response", G_CALLBACK(gtk_widget_destroy), dialog);
        gtk_widget_show(dialog);
    }
    g_clear_error(&error);
}

static void update_button(GthBrowser *browser) {
    GtkWidget *button = g_object_get_data(G_OBJECT(browser), "dotfiles-trim-button");
    if (!button) return;
    gboolean enabled = is_video(browser);
    gtk_widget_set_visible(button, enabled);
    gth_window_enable_action(GTH_WINDOW(browser), "trim-video", enabled);
}

static void construct(GthBrowser *browser) {
    const GActionEntry actions[] = { { .name = "trim-video", .activate = trim_video } };
    g_action_map_add_action_entries(G_ACTION_MAP(browser), actions, G_N_ELEMENTS(actions), browser);
    GtkWidget *button = gth_browser_add_header_bar_label_button(browser,
        GTH_BROWSER_HEADER_SECTION_VIEWER_COMMANDS, "Trim Video",
        "Open this video in Video Trimmer and close this window", "win.trim-video", NULL);
    gtk_widget_set_no_show_all(button, TRUE);
    g_object_set_data(G_OBJECT(browser), "dotfiles-trim-button", button);
    update_button(browser);
}

G_MODULE_EXPORT void gthumb_extension_activate(void) {
    gth_hook_add_callback("gth-browser-construct", 50, G_CALLBACK(construct), NULL);
    gth_hook_add_callback("gth-browser-update-sensitivity", 50, G_CALLBACK(update_button), NULL);
}
G_MODULE_EXPORT void gthumb_extension_deactivate(void) {}
G_MODULE_EXPORT gboolean gthumb_extension_is_configurable(void) { return FALSE; }
G_MODULE_EXPORT void gthumb_extension_configure(GtkWindow *parent) {}
