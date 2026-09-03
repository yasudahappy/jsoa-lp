# jsoa.net の DNS 記録

移行作業前の状態を控えたもの。**何かおかしくなったらこの状態に戻す。**

- レジストラ：Squarespace（`account.squarespace.com` → ドメイン → jsoa.net → DNS）
- 有効期限：2027年8月26日（自動更新オン）
- ネームサーバー：Squarespace のまま（**移さない方針**）
- 控えた日：2026年9月2日

## 移行前の状態

Squarespace の管理画面はレコードを3つのグループに分けて表示する。
**メール関連は「カスタムレコード」にあり、Squarespace 関連とは別グループ。**
そのため既定値グループを丸ごと削除してもメールに影響しない。

### Squarespaceの既定値（→ 削除する）

| タイプ | 名前 | 優先度 | TTL | データ |
|---|---|---|---|---|
| A | @ | — | 4時間 | 198.185.159.144 |
| A | @ | — | 4時間 | 198.185.159.145 |
| A | @ | — | 4時間 | 198.49.23.144 |
| A | @ | — | 4時間 | 198.49.23.145 |
| CNAME | www | — | 4時間 | ext-sq.squarespace.com |
| HTTPS | @ | — | 4時間 | `1 . alpn="h2,http/1.1" ipv4hint="198.185.159.144,198.18…"` |

> **HTTPS レコードを残さないこと。** SVCB/HTTPS レコードは `ipv4hint` に接続先IPを
> 内部で持つため、A レコードだけ差し替えて残すと一部のブラウザが Squarespace に
> 接続し続ける。グループのゴミ箱アイコンで一括削除すれば同時に消える。

### Squarespace Domain Connect（残しても害はない）

| タイプ | 名前 | TTL | データ |
|---|---|---|---|
| CNAME | _domainconnect | 1時間 | _domainconnect.domains.squarespace.com |

### カスタムレコード（→ **絶対に触らない**）

Google Workspace のメール（`info@jsoa.net`）が依存している。
1つでも消すとメールが止まり、予約の確定メールも協会の連絡先も失われる。

| タイプ | 名前 | 優先度 | TTL | データ |
|---|---|---|---|---|
| MX | @ | 1 | 1時間 | smtp.google.com |
| TXT | @ | — | 1時間 | `v=spf1 include:_spf.google.com ~all` |
| TXT | google._domainkey | — | 1時間 | `v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFA…`（管理画面上で省略表示。全文は控えていないので**編集も削除もしない**） |

## 移行後にすること

1. 「Squarespaceの既定値」グループを削除
2. カスタムレコードに追加
   - `A` / `@` / Netlify が指定するIP（通常 `75.2.60.5`）
   - `CNAME` / `www` / `<サイト名>.netlify.app`
3. Netlify 側で `jsoa.net` を主ドメインに設定（`www` はそこへリダイレクトされる）
4. HTTPS証明書が自動発行されるのを待つ

TTL が4時間なので、反映に最大4時間かかる。
