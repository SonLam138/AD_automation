// components/EventBubble.jsx

//import "./EventBubble.css";

function EventBubble({
    event
}) {

    if (
        event?.event_name !==
        "DETECTION_RESULT"
    ) {
        return null;
    }

    return (
        <div className="event-bubble">

            <div className="event-title">
                🎯 Ngáo nhận diện
            </div>

            <div className="event-row">
                <b>Action:</b>
                {" "}
                {event.detected_action}
            </div>

            {
                Object.entries(
                    event.detected_keywords || {}
                ).map(
                    ([key, value]) => (
                        <div
                            key={key}
                            className="event-row"
                        >
                            <b>{key}:</b>
                            {" "}
                            {value}
                        </div>
                    )
                )
            }

            <div className="event-feedback">
                Em nhận diện đúng chưa?
            </div>

            <div className="event-actions">

                <button>
                    👍 Đúng
                </button>

                <button>
                    👎 Sai
                </button>

            </div>

        </div>
    );
}

export default EventBubble;