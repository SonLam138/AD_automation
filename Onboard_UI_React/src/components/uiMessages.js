export const ACTIVE_ACTION_MESSAGES = [

    'Anh/chị vui lòng xử lý giúp Ngáo qua nút "Confirm" nhé ạ.',

    'Ngáo đang chờ xác nhận từ anh/chị trước khi tiếp tục 😄',

    'Thông tin đã đầy đủ rồi, chỉ cần bấm "Confirm" là được ạ.',

    'Hành động đang ở trạng thái chờ xác nhận. Vui lòng sử dụng card bên dưới.',

    'Ngáo chưa thể tiếp tục khi thao tác hiện tại chưa hoàn thành.',

    'Anh/chị hãy hoàn thành bước hiện tại trên card trước nhé 👑',

    'Card xác nhận đang sẵn sàng. Ngáo xin phép đợi ạ 😄'
];

export function getRandomMessage(
    messages
) {

    return messages[
        Math.floor(
            Math.random() * messages.length
        )
    ];

}