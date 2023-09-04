from pyrogram import Client, filters
from pyrogram.types import ChatMember, ChatPrivileges
from info import ADMINS


# Define a dictionary to map privilege names
privilege_names = {
    ChatPrivileges.can_manage_chat: "Manage Chat",
    ChatPrivileges.can_delete_messages: "Delete Messages",
    ChatPrivileges.can_manage_video_chats: "Manage Video Chats",
    ChatPrivileges.can_restrict_members: "Restrict Members",
    ChatPrivileges.can_promote_members: "Promote Members",
    ChatPrivileges.can_change_info: "Change Group Info",
    ChatPrivileges.can_send_messages: "Send Messages",
    ChatPrivileges.can_send_media_messages: "Send Media Messages",
    ChatPrivileges.can_send_other_messages: "Send Other Messages",
    ChatPrivileges.can_add_web_page_previews: "Add Web Page Previews",
    ChatPrivileges.can_send_polls: "Send Polls",
    ChatPrivileges.can_pin_messages: "Pin Messages",
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
        if isinstance(member.status, (ChatMember.Administrator, ChatMember.Owner)):
            admin_info = f"{member.user.mention} - {member.user.first_name}\n"
            privileges = []
            for privilege, privilege_name in privilege_names.items():
                if member.has_privilege(privilege):
                    privileges.append(privilege_name)
            if privileges:
                admin_info += "Privileges: " + ", ".join(privileges)
            admins.append(admin_info)

    if not admins:
        await message.reply("There are no administrators in this chat.")
        return

    response_message = f"Admins in {chat.title}:\n\n" + "\n\n".join(admins)
    await message.reply(response_message)
