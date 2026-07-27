const VERIFY_SECRET_MESSAGES = [
    "Ngáo em đang kiểm tra Admin Secret và thực hiện. Em sẽ thông báo lại Anh/chị.🤖 Đang thực hiện...",
    "Em Ngáo đang xác thực lại quyền, anh/chị chờ lát nhé. Em sẽ thông báo lại.🤖 Đang thực hiện...",
    "Hoàn hảo. Phê duyệt và hành động đang được thực hiện. Anh/chị chờ Ngáo một lát.🤖 Đang thực hiện...",
    "Ngáo đang làm rồi, Ngáo sẽ thông báo cho Anh/chị sau nhé.🤖 Đang thực hiện...",
    "Ngáo cảm ơn Anh/chị, giờ Ngáo đi kiểm tra Secret xong sẽ thực hiện luôn, Ngáo sẽ thông báo lại Anh/chị sau.🤖 Đang thực hiện..."
];

export function getRandomVerifySecretMessage() {

    const index = Math.floor(
        Math.random() *
        VERIFY_SECRET_MESSAGES.length
    );

    return VERIFY_SECRET_MESSAGES[index];
}