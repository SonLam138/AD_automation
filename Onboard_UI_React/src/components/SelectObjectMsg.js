export const confirmReadyMessages = [
    "Em Ngáo hiểu rồi! Anh/chị kiểm tra lại thông tin và xác nhận giúp Ngáo nhé.",
    "Đối tượng đã được chọn thành công. Anh/chị vui lòng rà soát lại thông tin trước khi tiếp tục.",
    "Thông tin đã sẵn sàng. Bước tiếp theo là xác nhận hành động.",
    "Tôi đã cập nhật lựa chọn của anh/chị. Vui lòng xác nhận để hệ thống thực hiện."
];

export function getRandomConfirmReadyMessage() {

    return confirmReadyMessages[
        Math.floor(
            Math.random()
            * confirmReadyMessages.length
        )
    ];

}