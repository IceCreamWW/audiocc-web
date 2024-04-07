import argparse
import shutil
from typing import List
from dataclasses import dataclass
from pathlib import Path

import yaml
from ldap3 import ALL, Connection, Server

parser = argparse.ArgumentParser(description="Collect user information from LDAP")
parser.add_argument("--output", "-o", type=str, default="workspace/users")
args = parser.parse_args()

teacher_group = "cn=users.identity.teacher.advisor,ou=groups,dc=sjtu,dc=edu,dc=cn"
student_group = "cn=users.identity.student,ou=groups,dc=sjtu,dc=edu,dc=cn"
default_avatar = "./default_avatar.png"

# LDAP服务器设置
server_uri = "ldap://localhost:389"
admin_dn = "cn=ldapservice,dc=sjtu,dc=edu,dc=cn"
admin_password = "ZmgTOe4sIa@ZEiyw"
search_base = "dc=sjtu,dc=edu,dc=cn"
search_filter = "(&(objectClass=user)(ak-active=true))"

# 建立LDAP连接
server = Server(server_uri, get_info=ALL)
conn = Connection(server, admin_dn, admin_password, auto_bind=True)

# 执行查询
conn.search(search_base, search_filter, attributes=["*", "+"])
entries = conn.entries


@dataclass
class User:
    role: str
    name_zh: str
    name_en: str
    enroll_date: str
    join_date: str
    degree: str
    avatar: str
    email: str
    fields: List
    intro_zh: str
    intro_en: str
    account: str

    def page(self, lang="en"):
        fields = {
            "role": self.role,
            "name": self.name_zh if lang == "zh" else self.name_en,
            "degree": self.degree,
            "fields": self.fields,
            "enroll_date": self.enroll_date,
            "join_date": self.join_date,
            "avatar": "avatar.png",
            "email": self.email,
        }
        content = "---\n" + yaml.dump(fields, default_flow_style=False, allow_unicode=True) + "---\n"
        if lang == "zh":
            content += self.intro_zh
        else:
            content += self.intro_en
        return content


users = []

# 处理查询结果
for entry in entries:
    print(entry.name)
    print(entry["memberOf"])
    if not entry["memberOf"]:
        continue

    if (
        not student_group in entry["memberOf"].value
        and not teacher_group in entry["memberOf"].value
    ):
        continue

    if teacher_group in entry["memberOf"].value:
        role = "teacher"
    else:
        role = "student"

    user = User(
        role="student",
        account=entry["sAMAccountName"].value,
        name_zh=entry["chinese_name"].value,
        name_en=entry["displayName"].value,
        fields=entry["fields"].value if "fields" in entry else [],
        enroll_date=entry["enrollment"].value if "enrollment" in entry else "unknown",
        join_date=entry["joined"].value if "joined" in entry else "unknown",
        degree=entry["degree"].value if "degree" in entry else "",
        avatar="/root/www/authentik/media/user-avatars/" + entry["avatar"].value.split("/")[-1] if "avatar"  in entry else default_avatar,
        email=entry["mail"].value,
        intro_zh=entry["introduction"].value if "introduction" in entry else "",
        intro_en=entry["introduction"].value if "introduction" in entry else "",
    )
    users.append(user)

workspace = Path(args.output)
for user in users:
    user_dir = workspace / user.account
    user_dir.mkdir(parents=True, exist_ok=True)
    with open(user_dir / "member.en.md", "w") as f:
        f.write(user.page("en"))
    with open(user_dir / "member.zh.md", "w") as f:
        f.write(user.page("zh"))

    shutil.copy(user.avatar, user_dir / "avatar.png")
