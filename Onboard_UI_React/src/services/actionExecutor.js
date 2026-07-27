// MAPING VỚI CAC API AD_TOOLS ĐỂ CONFIRM ACTION CARD TỰ ĐỘNG GỌI THEO ACTION KHÁC NHAU
import {
    disableUser,
    addGroup,
    removeGroup,
    moveUser
} from "./adToolApi";

const ACTION_MAP = {

    disable_user: disableUser,

    add_group: addGroup,
    add_group_member: addGroup,

    remove_group: removeGroup,
    remove_group_member: removeGroup,

    move_user: moveUser,
    move_user_to_ou: moveUser
};

export async function executeAction(
    action,
    payload
) {

    const executor =
        ACTION_MAP[action];

    if (!executor) {

        throw new Error(
            `Unsupported action: ${action}`
        );
    }

    return await executor(payload);
}


