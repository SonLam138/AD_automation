import {
    useState,
    useRef,
    useEffect
} from "react";

import "./chatpage.css";
import { sendMessage } from "../services/chatApi";
import GroupSelector from "../services/GroupSelector";
import ConfirmActionCard from "../cards/ConfirmActionCard";
import MultiConfirmCard from "../cards/MultiConfirmCard";

import {
    ACTIVE_ACTION_MESSAGES,
    getRandomMessage
}
from "../components/uiMessages";
import ObjectSelector from "../services/ObjectSelector";
import MultiSelector from "../services/MultiSelector";
import {getRandomConfirmReadyMessage, confirmReadyMessages} from "../components/SelectObjectMsg";

import {
    getCurrentUserName
}
from "../components/jwtHelper";

const LOADING_MESSAGES = [
    "🤔 Ngáo đang phân tích yêu cầu...",
    "📋 Đang đối chiếu thông tin trong Active Directory...",
    "🔍 Đang rà soát đối tượng liên quan...",
    "🧠 Đang suy nghĩ phương án xử lý...",
    "☕ Cho Ngáo thêm vài giây nhé..."
];


function ChatPage() {
    const displayName = getCurrentUserName();
    console.log(
    "DISPLAY NAME =",
    displayName
    );
    const [messages, setMessages] = useState([]);
    useEffect(() => {
        if (messages.length === 0) {
            setMessages([
                {
                    sender: "assistant",
                    text: `Xin chào ${displayName}. Em Ngáo trợ lý AD Automation Framework giúp gì được anh/chị ạ`
                }
            ]);
        }
    }, []);

    const messagesEndRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [input, setInput] = useState("");
    const [loadingMessage, setLoadingMessage] =
    useState(
        LOADING_MESSAGES[0]
    );

    const [activeAction, setActiveAction] = useState(null);
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    }, [messages, loading]);


    useEffect(() => {

        if (!loading) {
            return;
        }

        let index = 0;

        const interval = setInterval(() => {

            index++;

            if (
                index < LOADING_MESSAGES.length
            ) {
                setLoadingMessage(
                    LOADING_MESSAGES[index]
                );
            }

        }, 30000);

        return () => clearInterval(
            interval
        );

    }, [loading]);




    const handleSend = async () => {

        if (activeAction) {

            setMessages(prev => [
                ...prev,
                {
                    sender: "assistant",
                    text: getRandomMessage(ACTIVE_ACTION_MESSAGES)
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

        setLoadingMessage(
            LOADING_MESSAGES[0]
        );
        
        setLoading(true);

        try {
            console.log("Calling backend...");

            const result = await sendMessage(userText);

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
        if (
            result.state === "CONFIRM_READY" ||
            result.state === "WAITING_OBJECT_SELECTION"
        ) {

            setActiveAction({
                actionId: result.action_id,
                state: result.state
            });

        } else {

    setActiveAction(null);
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

    const handleObjectSelect = (
        resolverData,
        selectedObject
    ) => {
        const payload = 
            buildSinglePayload(
            resolverData.target_object_type,
            selectedObject,
            resolverData.proposed_action_payload
            );

        if (resolverData.new_value) {
            payload.new_value =
                resolverData.new_value;
        }
        console.log(
            "resolverData",
            resolverData
        );

        console.log(
            "payload",
            payload
        );

        const resolvedObjects = {
            ...resolverData.resolved_objects,
            [resolverData.target_object_type]:
            selectedObject
            };

        const approvalPolicy =
            getMultiApprovalPolicy(
                resolvedObjects
            );
            

        const confirmData = {
        ...resolverData,
            
        status: "READY_TO_CONFIRM",

        state: "CONFIRM_READY",

        next_step: "CONFIRM_ACTION",

        resolved_objects: {
            ...resolverData.resolved_objects,
            [resolverData.target_object_type]: selectedObject
        },

        candidate_objects: {},

        proposed_action_payload: payload,

        approval_policy: approvalPolicy

    };

        setActiveAction({
            actionId: resolverData.action_id,
            state: "CONFIRM_READY"
        });

        setMessages(prev => {

            const updated = prev.map(msg => {
            
                if (
                    msg.type ===
                    "WAITING_OBJECT_SELECTION"
                    ) {
                    const updatedMsg = {
                    ...msg,
                    data: {
                    ...msg.data,
                    completed: true,
                    selectedObject
                    }
                    };
                    return updatedMsg;
                    }
                    return msg;
                    });

            return [

                ...updated,

                {
                    sender: "assistant",
                    text:
                        getRandomConfirmReadyMessage()
                },

                {
                    type: "CONFIRM_READY",
                    data: confirmData
                }

            ];

        });

    };

    const handleGroupSelect = (
    resolverData,
    selectedGroup
) => {
    const confirmData = {
    ...resolverData,
        
    status: "READY_TO_CONFIRM",

    state: "CONFIRM_READY",

    next_step: "CONFIRM_ACTION",

    resolved_objects: {
        ...resolverData.resolved_objects,
        GROUP: selectedGroup
            },

    candidate_objects: {},

    proposed_action_payload:
        buildSinglePayload(
            resolverData.target_object_type,
            selectedObject,
            resolverData.proposed_action_payload
        )

    };

    setActiveAction({
        actionId: resolverData.action_id,
        state: "CONFIRM_READY"
    });

    setMessages(prev => {

        const updated = prev.map(msg => {
        
            if (
                msg.type ===
                "WAITING_OBJECT_SELECTION"
                ) {
                const updatedMsg = {
                ...msg,
                data: {
                ...msg.data,
                completed: true,
                selectedGroup
                }
                };
                return updatedMsg;
                }
                return msg;
                });

        return [

            ...updated,

            {
                sender: "assistant",
                text:
                    getRandomConfirmReadyMessage()
            },

            {
                type: "CONFIRM_READY",
                data: confirmData
            }
            ];
        });
    };

    const handleMultiSelect = (
        resolverData,
        objectType,
        selectedObject
    ) => {

        console.log(
            "OBJECT TYPE =",
            objectType
            );
        console.log(
            "SELECTED OBJECTS BEFORE =",
            resolverData.selected_objects
            );

        const requiredObjectTypes =
            Object.keys(
                resolverData.candidate_objects || {}
            );

        const currentSelectedObjects = {
            ...(resolverData.selected_objects || {}),
            [objectType]: selectedObject
        };
        console.log(
            "CURRENT SELECTED OBJECTS =",
            currentSelectedObjects
            );

        const allSelected =
            requiredObjectTypes.every(
                objType =>
                    currentSelectedObjects[objType]
            );

        if (!allSelected) {
            setMessages(prev => {

                return prev.map(msg => {

                    if (
                        msg.type === "WAITING_OBJECT_SELECTION"
                    ) {
                        return {
                            ...msg,
                            data: {
                                ...msg.data,
                                selected_objects:
                                    currentSelectedObjects
                            }
                        };
                    }

                    return msg;
                });

            });

            return;
        }

        const resolvedObjects = {
            ...currentSelectedObjects
        };
        const approvalPolicy =
            getMultiApprovalPolicy(
                resolvedObjects
            );

        const proposedActionPayload =
            buildActionPayload(
                resolverData.action,
                resolvedObjects
            );

        const confirmData = {

            ...resolverData,

            status: "READY_TO_CONFIRM",

            state: "CONFIRM_READY",

            next_step: "CONFIRM_ACTION",

            completed: true,

            resolved_objects: resolvedObjects,

            selected_objects:
                currentSelectedObjects,

            proposed_action_payload:
                proposedActionPayload,

            approval_policy: approvalPolicy
        };

        setActiveAction({
            actionId: resolverData.action_id,
            state: "CONFIRM_READY"
        });

        setMessages(prev => {

            return prev.map(msg => {

                if (
                    msg.type === "WAITING_OBJECT_SELECTION"
                ) {
                    return {
                        ...msg,
                        data: confirmData
                    };
                }

                return msg;
            });

        });
    };

    function getMultiApprovalPolicy(
        resolvedObjects
    ) {

        const objects =
            Object.values(
                resolvedObjects || {}
            );

        for (const item of objects) {

            if (
                item?.approval_policy ===
                "admin_secret"
            ) {
                return "admin_secret";
            }

        }

        return "normal";
    }

    function buildActionPayload(
        action,
        resolvedObjects
    ) {

        switch (action) {

            case "add_group_member":
                return {
                    sam_account_name:
                        resolvedObjects.USER.sam_account_name,

                    group_name:
                        resolvedObjects.GROUP.name
                };

            case "move_user_to_ou":
                return {
                    sam_account_name:
                        resolvedObjects.USER.sam_account_name,

                    target_ou_dn:
                        resolvedObjects.OU.distinguished_name
                };

            case "move_user_to_ou":
                return {
                    sam_account_name:
                        selectedUser.sam_account_name,

                    target_ou_dn:
                        proposedActionPayload.target_ou_dn
                };
            
            default:
                return {};
        }
    }

    function getActionParamValue(
        objectType,
        actionParam,
        item
    ) {

        if (objectType === "USER") {

            if (
                actionParam ===
                "sam_account_name"
            ) {
                return item.sam_account_name;
            }

            if (
                actionParam ===
                "user_dn"
            ) {
                return item.distinguished_name;
            }

        }

        if (objectType === "GROUP") {

            if (
                actionParam ===
                "group_name"
            ) {
                return (
                    item.cn ||
                    item.name
                );
            }

            if (
                actionParam ===
                "group_dn"
            ) {
                return item.distinguished_name;
            }

        }

        if (objectType === "OU") {

            if (
                actionParam ===
                "target_ou_dn"
            ) {
                return item.distinguished_name;
            }

            if (
                actionParam ===
                "ou"
            ) {
                return item.ou;
            }

        }

        if (objectType === "COMPUTER") {

            if (
                actionParam ===
                "computer_name"
            ) {
                return item.computer_name;
            }

        }

        return null;
    }


    function buildSinglePayload(
        objectType,
        selectedObject,
        existingPayload = {}
    ) {

        const payload = {
            ...existingPayload
        };

        if (objectType === "USER") {

            payload.sam_account_name =
                selectedObject.sam_account_name;

        }

        if (objectType === "GROUP") {

            payload.group_name =
                selectedObject.cn ||
                selectedObject.name;

        }

        if (objectType === "OU") {

            payload.target_ou_dn =
                selectedObject.distinguished_name;

        }

        if (objectType === "COMPUTER") {

            payload.computer_name =
                selectedObject.computer_name;

        }

        return payload;
    }


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
                            <p>Ngáo em xin chào anh/chị</p>
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
                    if (
                        msg.type === "WAITING_OBJECT_SELECTION"
                    ) {
                        const candidateObjectTypes =
                            Object.keys(
                                msg.data?.candidate_objects || {}
                            );

                        const resolvedObjectTypes =
                            Object.keys(
                                msg.data?.resolved_objects || {}
                            );

                        const isMultiFlow =
                            candidateObjectTypes.length > 1
                            ||
                            (
                                msg.data?.completed === true
                                &&
                                resolvedObjectTypes.length > 1
                            );

                        console.log(
                            "MULTI FLOW =",
                            isMultiFlow
                        );

                        if (isMultiFlow) {

                            if (msg.data?.completed) {
                                return (
                                    <MultiConfirmCard
                                        key={idx}
                                        data={msg.data}
                                        onVerifyMessage={(message) => {

                                            setMessages(prev => [
                                                ...prev,
                                                {
                                                    sender: "assistant",
                                                    text: message
                                                }
                                            ]);

                                        }}
                                        onFinished={(result) => {

                                            setActiveAction(null);

                                            setMessages(prev => [
                                                ...prev,
                                                {
                                                    sender: "assistant",
                                                    text: result.message
                                                }
                                            ]);

                                        }}
                                        onCancel={() => {
                                            setActiveAction(null);
                                        }}
                                    />
                                );
                            }

                            return (
                                <MultiSelector
                                    key={idx}
                                    Data={msg.data}
                                    onSelect={handleMultiSelect}
                                />
                            );
                        }
                        

                        if (
                            msg.data?.target_object_type
                            === "GROUP"
                            ) {
                            return (
                            <GroupSelector
                                key={idx}
                                Data={msg.data}
                                onSelect={handleGroupSelect}
                            />
                            );
                            }

                        return (
                            <ObjectSelector
                                key={idx}
                                Data={msg.data}
                                onSelect={handleObjectSelect}
                            />
                        );
                    }

                    if (
                        msg.type === "CONFIRM_READY"
                    ) {
                        return (
                            <ConfirmActionCard
                                key={idx}
                                data={msg.data}
                                onVerifyMessage={(message) => {

                                    setMessages(prev => [
                                        ...prev,
                                        {
                                            sender: "assistant",
                                            text: message
                                        }
                                    ]);

                                }}
                                onFinished={(result) => {

                                    setActiveAction(null);

                                    setMessages(prev => [
                                        ...prev,
                                        {
                                            sender: "assistant",
                                            text: result.message
                                        }
                                    ]);

                                }}
                                onCancel={() => {
                                setActiveAction(null);
                                }}
                            />
                        );
                    }

                    if (
                        msg.text === undefined
                        || msg.text === null
                        || msg.text === ""
                    ) {
                        return null;
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
                        {loadingMessage}
                    </div>
                )}
                <div ref={messagesEndRef}></div>

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