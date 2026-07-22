import { useState } from "react";
import "./chatpage.css";
import { sendMessage } from "../services/chatApi";
import ConfirmActionCard from "../cards/ConfirmActionCard";

function ChatPage() {
    const [messages, setMessages] = useState([
        {
            sender: "assistant",
            text: "Xin chào. Tôi là trợ lý AD Automation Framework."
        }
    ]);
    const [loading, setLoading] = useState(false);
    const [input, setInput] = useState("");
    const [activeAction, setActiveAction] = useState(null);

    const handleSend = async () => {
        console.log(
        "ACTIVE ACTION =",
        activeAction
    );
        console.log("HANDLE SEND CALLED");
        if (activeAction) {

            setMessages(prev => [
                ...prev,
                {
                    sender: "assistant",
                    text: 'Anh/chị vui lòng xử lý giúp Ngáo qua nút "Confirm" nhé ạ.'
                }
            ]);

            setInput("");

            return;
        }


        if (!input.trim()) return;

        const userText = input;

        setMessages(prev => [
            ...prev,
            {
                sender: "user",
                text: userText
            }
        ]);

        setInput("");

        setLoading(true);

        try {
            console.log("Calling backend...");

            const result = await sendMessage(userText);

            console.log(result);


            setMessages(prev => [
            ...prev,

            {
                sender: "assistant",
                text: result.message
            },

            {
                sender: "assistant",
                type: result.state,
                data: result
            }
        ]);
        if (result.state) {

            setActiveAction({
                actionId: result.action_id,
                state: result.state
            });
        }


        } catch (error) {

            setMessages(prev => [
                ...prev,
                {
                    sender: "assistant",
                    text: "Không thể kết nối trợ lý."
                }
            ]);

        } finally {

            setLoading(false);

        }
    };

    return (
        <div className="chat-page">

            <div className="chat-header">

                <div className="assistant-header">

                    <div className="assistant-left">

                        <img
                            src="/ngao.png"
                            alt="Ngao"
                            className="assistant-avatar"
                        />

                        <div className="assistant-info">
                            <h2>AD Automation Assistant</h2>
                            <p>Ready</p>
                        </div>

                    </div>

                    <button
                        className="back-btn"
                        onClick={() => navigate("/portal/ai-lab")}
                    >
                        ← Portal
                    </button>

                </div>

            </div>

            <div className="chat-body">

            {messages.map((msg, idx) => {

                if (msg.type === "CONFIRM_READY") {
                    return (
                        <ConfirmActionCard
                            key={idx}
                            data={msg.data}
                            onFinished={(result) => {                                    
                                    setActiveAction(null);                                   
                                    setMessages(prev => [
                                        ...prev,
                                        {
                                            sender: "assistant",
                                            text:
                                                result.message
                                        }
                                    ]);
                                }}
                        />
                    );
                }

                return (
                    <div
                        key={idx}
                        className={`message ${msg.sender}`}
                    >
                        {msg.text}
                    </div>
                );

            })}
                    {loading && (

                        <div className="message assistant loading-bubble">
                            🤖 Ngáo đang suy nghĩ...
                        </div>

                    )}

                </div>

            <div className="chat-footer">
                <input
                    type="text"
                    value={input}
                    placeholder="Nhập nội dung..."
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            handleSend();
                        }
                    }}
                />

                <button onClick={handleSend}>
                    Gửi
                </button>
            </div>

        </div>
    );
}

export default ChatPage;