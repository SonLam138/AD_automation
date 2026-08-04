
// Tạm thời chưa dùng

import { EVENT_REGISTRY } from "./eventRegistry";

function EventRenderer({
    event
}) {

    const Component =
        EVENT_REGISTRY[
            event.event_name
        ];

    if (!Component) {
        return null;
    }

    return (
        <Component
            event={event}
        />
    );
}

export default EventRenderer;