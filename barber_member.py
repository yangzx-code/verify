import json
import os


def yuan_to_fen(amount):
    return int(round(float(amount) * 100))


def fen_to_yuan(fen):
    return fen / 100


class Member:
    def __init__(self, member_id, name, phone, balance=0):
        self.id = member_id
        self.name = name
        self.phone = phone
        self.balance = int(balance)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "balance": fen_to_yuan(self.balance)
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["name"],
            data["phone"],
            yuan_to_fen(data["balance"])
        )


class MemberManager:
    def __init__(self, data_file="members.json"):
        self.data_file = data_file
        self.members = {}
        self.next_id = 1
        self.load()

    def load(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data.get("members", []):
                member = Member.from_dict(item)
                self.members[member.id] = member
            self.next_id = data.get("next_id", 1)

    def save(self):
        data = {
            "next_id": self.next_id,
            "members": [m.to_dict() for m in self.members.values()]
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_member(self, name, phone):
        for member in self.members.values():
            if member.phone == phone:
                print(f"错误：电话 {phone} 已注册！")
                return None
        member = Member(self.next_id, name, phone)
        self.members[self.next_id] = member
        self.next_id += 1
        self.save()
        print(f"会员注册成功！ID: {member.id}")
        return member

    def get_member(self, member_id):
        return self.members.get(member_id)

    def get_member_by_phone(self, phone):
        for member in self.members.values():
            if member.phone == phone:
                return member
        return None

    def recharge(self, member_id, amount):
        member = self.get_member(member_id)
        if not member:
            print(f"错误：会员ID {member_id} 不存在！")
            return False
        if yuan_to_fen(amount) <= 0:
            print("错误：充值金额必须大于0！")
            return False
        member.balance += yuan_to_fen(amount)
        self.save()
        print(f"充值成功！当前余额: {fen_to_yuan(member.balance):.2f} 元")
        return True

    def consume(self, member_id, amount):
        member = self.get_member(member_id)
        if not member:
            print(f"错误：会员ID {member_id} 不存在！")
            return False
        if yuan_to_fen(amount) <= 0:
            print("错误：消费金额必须大于0！")
            return False
        if member.balance < yuan_to_fen(amount):
            print(f"错误：余额不足！当前余额: {fen_to_yuan(member.balance):.2f} 元")
            return False
        member.balance -= yuan_to_fen(amount)
        self.save()
        print(f"消费成功！当前余额: {fen_to_yuan(member.balance):.2f} 元")
        return True

    def list_all_members(self):
        if not self.members:
            print("暂无会员")
            return
        print("\n" + "="*60)
        print(f"{'ID':<5} {'姓名':<10} {'电话':<15} {'余额':>10}")
        print("-"*60)
        for member in self.members.values():
            print(f"{member.id:<5} {member.name:<10} {member.phone:<15} {fen_to_yuan(member.balance):>9.2f} 元")
        print("="*60)

    def delete_member(self, member_id):
        if member_id not in self.members:
            print(f"错误：会员ID {member_id} 不存在！")
            return False
        member = self.members.pop(member_id)
        self.save()
        print(f"会员删除成功！ID: {member.id}, 姓名: {member.name}")
        return True

    def update_member(self, member_id, name=None, phone=None):
        member = self.get_member(member_id)
        if not member:
            print(f"错误：会员ID {member_id} 不存在！")
            return False
        if phone and phone != member.phone:
            for m in self.members.values():
                if m.phone == phone:
                    print(f"错误：电话 {phone} 已注册！")
                    return False
        if name:
            member.name = name
        if phone:
            member.phone = phone
        self.save()
        print(f"会员信息修改成功！")
        print(f"ID: {member.id}, 姓名: {member.name}, 电话: {member.phone}")
        return True

    def count_members(self):
        return len(self.members)


def print_menu():
    print("\n" + "="*40)
    print("理发店会员管理系统")
    print("="*40)
    print("1. 添加会员")
    print("2. 会员充值")
    print("3. 会员消费")
    print("4. 查询会员信息")
    print("5. 修改会员信息")
    print("6. 显示所有会员")
    print("7. 删除会员")
    print("0. 退出系统")
    print("="*40)


def main():
    manager = MemberManager()
    print(f"系统启动成功，当前会员数: {manager.count_members()}")

    while True:
        print_menu()
        try:
            choice = input("\n请选择操作: ").strip()

            if choice == "0":
                print("感谢使用，再见！")
                break

            elif choice == "1":
                name = input("请输入姓名: ").strip()
                phone = input("请输入电话: ").strip()
                if name and phone:
                    manager.add_member(name, phone)
                else:
                    print("错误：姓名和电话不能为空！")

            elif choice == "2":
                try:
                    mid = int(input("请输入会员ID: "))
                    amount = float(input("请输入充值金额: "))
                    manager.recharge(mid, amount)
                except ValueError:
                    print("错误：请输入有效的数字！")

            elif choice == "3":
                try:
                    mid = int(input("请输入会员ID: "))
                    amount = float(input("请输入消费金额: "))
                    manager.consume(mid, amount)
                except ValueError:
                    print("错误：请输入有效的数字！")

            elif choice == "4":
                try:
                    mid = int(input("请输入会员ID: "))
                    member = manager.get_member(mid)
                    if member:
                        print("\n会员信息:")
                        print(f"ID: {member.id}")
                        print(f"姓名: {member.name}")
                        print(f"电话: {member.phone}")
                        print(f"余额: {fen_to_yuan(member.balance):.2f} 元")
                    else:
                        print(f"错误：会员ID {mid} 不存在！")
                except ValueError:
                    print("错误：请输入有效的数字！")

            elif choice == "5":
                try:
                    mid = int(input("请输入会员ID: "))
                    member = manager.get_member(mid)
                    if member:
                        print(f"\n当前信息: ID:{member.id}, 姓名:{member.name}, 电话:{member.phone}")
                        print("(直接回车表示不修改)")
                        name = input("请输入新姓名: ").strip()
                        phone = input("请输入新电话: ").strip()
                        if name or phone:
                            manager.update_member(mid, name if name else None, phone if phone else None)
                        else:
                            print("未修改任何信息")
                    else:
                        print(f"错误：会员ID {mid} 不存在！")
                except ValueError:
                    print("错误：请输入有效的数字！")

            elif choice == "6":
                manager.list_all_members()

            elif choice == "7":
                try:
                    mid = int(input("请输入要删除的会员ID: "))
                    manager.delete_member(mid)
                except ValueError:
                    print("错误：请输入有效的数字！")

            else:
                print("错误：无效的选择，请输入0-7之间的数字！")

        except KeyboardInterrupt:
            print("\n\n感谢使用，再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
