from marshmallow import fields, post_dump

class ShareLinkMixin:
    """
    リソースに紐づく共有リンクを権限ごとにフィルタし、
    各アクセスレベルのショートカットキーを展開するMixin。
    対象スキーマで group_links や tournament_links などの
    List(Nested(ShareLinkSchema)) フィールドを定義しておく必要がある。
    """

    # ショートカットキー
    view_link = fields.Str(dump_only=True, description="閲覧用キー")
    edit_link = fields.Str(dump_only=True, description="編集用キー")
    owner_link = fields.Str(dump_only=True, description="管理者用キー")

    # このMixinを継承するスキーマで「linksフィールド名」を指定する必要あり
    _share_link_field_name = None  # e.g., "group_links", "tournament_links"

    @post_dump(pass_original=True)
    def filter_links_and_extract_shortcuts(self, data, original_obj, **kwargs):
        """ユーザー権限に応じて共有リンクをフィルタし、ショートカットを設定"""

        field_name = getattr(self, "_share_link_field_name", None)
        if not field_name or field_name not in data:
            return data  # このMixinを適用しないスキーマ

        links = data.get(field_name, [])
        user_access = getattr(original_obj, "current_user_access", None)
        # === アクセスレベルごとのリンク制限 ===
        if user_access == "VIEW":
            filtered = [l for l in links if l.get("access_level") == "VIEW"]
        elif user_access == "EDIT":
            filtered = [l for l in links if l.get("access_level") in ["VIEW", "EDIT"]]
        elif user_access == "OWNER":
            filtered = links
        else:
            filtered = []

        data[field_name] = filtered
        # === ショートカットキー設定 ===
        for l in filtered:
            level = l.get("access_level")
            key = l.get("short_key")
            if not key:
                continue
            if level == "VIEW":
                data["view_link"] = key
            elif level == "EDIT":
                data["edit_link"] = key
            elif level == "OWNER":
                data["owner_link"] = key

        return data
