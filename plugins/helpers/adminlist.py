from pyrogram import Client, filters
from pyrogram.types import ChatMember, ChatPermissions
from info import ADMINS

# Define a dictionary to map privilege names
privilege_names = {
    ChatPermissions.can_change_info: "Change Group Info",
    ChatPermissions.can_post_messages: "Send Messages",
    ChatPermissions.can_edit_messages: "Edit Messages",
    ChatPermissions.can_delete_messages: "Delete Messages",
    ChatPermissions.can_invite_users: "Invite Users",
    ChatPermissions.can_restrict_members: "Restrict Members",
    ChatPermissions.can_pin_messages: "Pin Messages",
    ChatPermissions.can_manage_chat: "Manage Chat",
    ChatPermissions.can_delete_messages: "Delete Messages",
    ChatPermissions.can_manage_video_chats: "Manage Video Chats",
    ChatPermissions.can_restrict_members: "Restrict Members",
    ChatPermissions.can_promote_members: "Promote Members",
    ChatPermissions.is_anonymous: "Anonymous Mode",
}

@Client.on_message(filters.command("admins") & filters.user(ADMINS))
async def list_admins(client, message):
    chat_id = message.text.split()[1]  # Extract the chat_id from the command, e.g., "/admins 12345"

    try:
        chat_id = int(chat_id)
    except ValueError:
        await message.reply("Invalid chat ID. Please use '/admins CHAT_ID' to list admins.")
        return

    # Get the chat members and filter for administrators
    chat = await client.get_chat(chat_id)
    admins = []

    async for member in client.iter_chat_members(chat_id):
        if isinstance(member.status, (ChatMemberAdministrator, ChatMemberOwner)):
            admin_info = f"{member.user.mention} - {member.user.first_name}\n"
            privileges = []
            for permission, privilege_name in privilege_names.items():
                if member.can(permission):
                    privileges.append(privilege_name)
            if privileges:
                admin_info += "Privileges: " + ", ".join(privileges)
            admins.append(admin_info)

    if not admins:
        await message.reply("There are no administrators in this chat.")
        return

    response_message = f"Admins in {chat.title}:\n\n" + "\n\n".join(admins)
    await message.reply(response_message)
