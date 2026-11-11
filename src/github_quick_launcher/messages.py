"""Every piece of text the plugin shows in Flow Launcher, in one place."""

from __future__ import annotations

PLUGIN_NAME = "Github Quick Launcher"

# Context menu: (title, subtitle). A subtitle of None shows the copied value.
MENU_OPEN_BROWSER = ("ブラウザで開く", "リポジトリをブラウザで開きます")
MENU_OPEN_DESKTOP = ("GitHub Desktop で開く", "リポジトリを GitHub Desktop で開きます")
MENU_OPEN_VSCODE = ("VS Code で開く", "リポジトリを VS Code でクローンして開きます")
MENU_COPY_NAME = "フルネームをコピー"
MENU_COPY_URL = "URL をコピー"
MENU_CLONE_HTTPS = "HTTPS のクローン URL をコピー"
MENU_CLONE_SSH = "SSH のクローン URL をコピー"
MENU_CLONE_CLI = "GitHub CLI のクローンコマンドをコピー"

SETTINGS_PROMPT_TITLE = "GitHub のユーザー名またはトークンを設定してください"
SETTINGS_PROMPT_SUBTITLE = "Enter で設定を開きます。設定後は「/」で自分のリポジトリを一覧できます"

RATE_LIMIT_TITLE = "GitHub API の利用上限に達しました"
RATE_LIMIT_SUBTITLE = "{resets} にリセットされます。Enter で設定を開き、トークンを追加すると上限が上がります"
BAD_TOKEN_TITLE = "GitHub がトークンを拒否しました"
BAD_TOKEN_SUBTITLE = "Enter で設定を開き、トークンを入れ直してください"
USER_NOT_FOUND_TITLE = "GitHub ユーザーが見つかりません"
USER_NOT_FOUND_SUBTITLE = "Enter で設定を開き、ユーザー名を確認してください"
OFFLINE_TITLE = "GitHub に接続できません"
OFFLINE_SUBTITLE = "ネットワーク接続を確認して、もう一度お試しください"
REQUEST_FAILED_TITLE = "GitHub へのリクエストに失敗しました"

ONLINE_OFF_TITLE = "オンライン検索はオフです"
ONLINE_OFF_SUBTITLE = "キャッシュ済みのリポジトリだけを検索しています。Enter で設定を変更できます"

REFRESH_TITLE = "リポジトリのキャッシュを更新"
REFRESH_SUBTITLE = "自分のリポジトリとスターを GitHub から取得し直します"
CLEAR_TITLE = "キャッシュしたリポジトリ一覧を削除"
CLEAR_SUBTITLE = "この PC に保存された自分のリポジトリとスターの一覧を削除します"

NEED_IDENTITY_MSG = "先に GitHub のユーザー名またはトークンを設定してください"
REFRESHED_MSG = "リポジトリのキャッシュを更新しました"
CLEARED_MSG = "キャッシュしたリポジトリ一覧を削除しました"

# Errors that reach the screen as a subtitle of REQUEST_FAILED_TITLE.
HTTP_STATUS_ERROR = "GitHub が HTTP {status} を返しました"
NOT_JSON_ERROR = "GitHub から JSON 以外の応答が返されました"
UNDECODABLE_ERROR = "GitHub からの応答を展開できませんでした"
OUTSIDE_API_ERROR = "GitHub API 以外へのリクエストは送信しません"
REFRESH_FAILED_ERROR = "更新に失敗しました: {error}"
