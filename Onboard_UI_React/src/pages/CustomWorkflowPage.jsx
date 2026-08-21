import "./CustomWorkflowPage.css";
import axiosClient from "../api/axiosClient";

import {
    useState
} from "react";

import {
    useNavigate
} from "react-router-dom";

export default function CustomWorkflowPage() {

    const navigate = useNavigate();
    const [workflowInfo, setWorkflowInfo] = useState({
        workflowName: "",
        description: "",
        workflowId:
            `WF_${Date.now()}`,
        context:
            `CUSTOM_WF_${Date.now()}`
    });

    const [objects, setObjects] = useState([]);
    const [validated, setValidated] = useState(false);


    const handleAddObject = () => {

        setObjects(prev => [
            ...prev,
            {
                id: Date.now(),

                alias: "",

                objectType: "USER",

                employee_id: "",

                username: "",

                group_name: "",

                email: "",

                computer_name: ""
            }
        ]);
    };
    
    const handleObjectChange = (
        id,
        field,
        value
    ) => {

        setValidated(false);

        setObjects(prev =>
            prev.map(obj =>
                obj.id === id
                    ? {
                        ...obj,
                        [field]: value
                    }
                    : obj
            )
        );
    };

    const handleRemoveObject = (id) => {

        setObjects(prev =>
            prev.filter(
                obj => obj.id !== id
            )
        );
    };

    const handleCreateFlow = () => {

        navigate(
            "/portal/workflow/custom/designer",
            {
                state: {
                    workflowInfo,
                    objects
                }
            }
        );

    };

    const handleValidate = async () => {
        if (!validateForm()) {
            return;
        }

        try {

            const payload = {
                workflowInfo,
                objects
            };

            const response =
                await axiosClient.post(
                    "/api/workflow/validate",
                    payload
                );

            if (response.data.success) {

                setValidated(true);

                alert(
                    "Validation success"
                );
                return;
            }
            setValidated(false);
            alert(
                "Validation failed"
                );

        } catch (error) {

            console.error(error);

            setValidated(false);

            alert(
                "Validation failed"
            );
        }
    };

    const validateForm = () => {

        if (!workflowInfo.workflowName.trim()) {
            alert("Workflow Name is required");
            return false;
        }

        if (objects.length === 0) {
            alert("At least one object is required");
            return false;
        }

        for (const obj of objects) {

            if (!obj.alias?.trim()) {
                alert("Alias is required");
                return false;
            }

            if (obj.objectType === "USER") {

                if (!obj.username?.trim()) {
                    alert(
                        `Username is required for ${obj.alias}`
                    );
                    return false;
                }

                if (!obj.email?.trim()) {
                    alert(
                        `Email is required for ${obj.alias}`
                    );
                    return false;
                }
            }

            if (obj.objectType === "GROUP") {

                if (!obj.group_name?.trim()) {
                    alert(
                        `Group Name is required for ${obj.alias}`
                    );
                    return false;
                }

                if (!obj.email?.trim()) {
                    alert(
                        `Email is required for ${obj.alias}`
                    );
                    return false;
                }
            }

            if (obj.objectType === "COMPUTER") {

                if (!obj.computer_name?.trim()) {
                    alert(
                        `Computer Name is required for ${obj.alias}`
                    );
                    return false;
                }
            }

            if (obj.objectType === "CREATE_NEW_USER") {

                if (!obj.username?.trim()) {
                    alert(
                        `Username is required for ${obj.alias}`
                    );
                    return false;
                }

                if (!obj.email?.trim()) {
                    alert(
                        `Email is required for ${obj.alias}`
                    );
                    return false;
                }
            }

            if (obj.objectType === "CREATE_NEW_GROUP") {

                if (!obj.group_name?.trim()) {
                    alert(
                        `Group Name is required for ${obj.alias}`
                    );
                    return false;
                }
            }
        }

        return true;
    };





    return (

        <div className="custom-workflow-page">

            <div className="custom-workflow-header">

                <h2>
                    Custom Workflow Builder
                </h2>

                <p>
                    Thiết kế workflow tùy chỉnh cho
                    Auto Engine.
                </p>
                <button
                    type="button"
                    className="validate-btn"
                    onClick={handleValidate}
                >
                    Validate
                </button>
                
                <button
                    className="create-flow-btn"
                    type="button"
                    onClick={handleCreateFlow}
                    disabled={!validated}
                >
                    Create Flow →
                </button>

            </div>

            <div className="custom-workflow-registration-layout">

                <div className="custom-card">

                    <h3>
                        Workflow Identity
                    </h3>

                    <div className="form-group">

                        <label>
                            Workflow Name
                            <span className="required">*</span>
                        </label>

                        <input
                            type="text"
                            value={workflowInfo.workflowName}
                            onChange={(e) =>{
                                setValidated(false);
                                setWorkflowInfo({
                                    ...workflowInfo,
                                    workflowName: e.target.value
                                });
                            }}
                        />

                    </div>
                    <div className="form-group">

                        <label>
                            Description
                        </label>

                        <textarea
                            rows={3}
                            value={workflowInfo.description}
                            onChange={(e) =>{
                                setValidated(false);
                                setWorkflowInfo({
                                    ...workflowInfo,
                                    description: e.target.value
                                });
                            }
                            }
                        />

                    </div>
                    <div className="form-group">

                        <label>
                            Workflow ID
                        </label>

                        <input
                            type="text"
                            value={workflowInfo.workflowId}
                            disabled
                        />

                    </div>
                    <div className="form-group">

                        <label>
                            Context
                        </label>

                        <input
                            type="text"
                            value={workflowInfo.context}
                            disabled
                        />

                    </div>
                    <div className="form-group">

                        <label>
                            Request Type
                        </label>

                        <input
                            type="text"
                            value="CUSTOM_WORKFLOW"
                            disabled
                        />

                    </div>

                </div>




                <div className="custom-card">

                    <div className="card-header">

                        <h3>
                            Object Catalog
                        </h3>
                        <small>
                            {objects.length} object(s)
                        </small>

                        <button
                            type="button"
                            onClick={handleAddObject}
                        >
                            + Add Object
                        </button>

                    </div>
                    {
                        objects.map((obj, index) => (

                            <div
                                key={obj.id}
                                className="object-item"
                            >
                                <div className="object-header">

                                    <strong>
                                        {obj.alias || `Object ${index + 1}`}
                                    </strong>

                                    <button classname="remove-object"
                                        type="button"
                                        onClick={() =>
                                            handleRemoveObject(obj.id)
                                        }
                                    >
                                        Remove
                                    </button>

                                </div>

                                <div className="form-group">

                                    <label>
                                        Alias
                                        <span className="required">*</span>
                                    </label>

                                    <input
                                        type="text"
                                        value={obj.alias}
                                        onChange={(e) =>
                                            handleObjectChange(
                                                obj.id,
                                                "alias",
                                                e.target.value
                                            )
                                        }
                                    />

                                </div>
                                <div className="form-group">

                                    <label>
                                        Object Type
                                    </label>

                                    <select
                                        value={obj.objectType}
                                        onChange={(e) =>
                                            handleObjectChange(
                                                obj.id,
                                                "objectType",
                                                e.target.value
                                            )
                                        }
                                    >

                                        <option value="USER">
                                            USER
                                        </option>

                                        <option value="GROUP">
                                            GROUP
                                        </option>

                                        <option value="COMPUTER">
                                            COMPUTER
                                        </option>

                                        <option value="CREATE_NEW_USER">
                                            CREATE_NEW_USER
                                        </option>
                                        <option value="CREATE_NEW_GROUP">
                                            CREATE_NEW_GROUP
                                        </option>

                                    </select>

                                </div>
                                {
                                    obj.objectType === "USER" && (
                                        <>

                                            <div className="form-group">

                                                <label>
                                                    Employee ID
                                                </label>

                                                <input
                                                    type="text"
                                                    value={obj.employee_id}
                                                    onChange={(e) =>
                                                        handleObjectChange(
                                                            obj.id,
                                                            "employee_id",
                                                            e.target.value
                                                        )
                                                    }
                                                />

                                            </div>

                                            <div className="form-group">

                                                <label>
                                                    Username
                                                    <span className="required">*</span>
                                                </label>

                                                <input
                                                    type="text"
                                                    value={obj.username}
                                                    onChange={(e) =>
                                                        handleObjectChange(
                                                            obj.id,
                                                            "username",
                                                            e.target.value
                                                        )
                                                    }
                                                />

                                            </div>

                                            <div className="form-group">

                                                <label>
                                                    Email
                                                    <span className="required">*</span>
                                                </label>

                                                <input
                                                    type="text"
                                                    value={obj.email}
                                                    onChange={(e) =>
                                                        handleObjectChange(
                                                            obj.id,
                                                            "email",
                                                            e.target.value
                                                        )
                                                    }
                                                />

                                            </div>

                                        </>
                                    )
                                }
                                {
                                    obj.objectType === "GROUP" && (
                                        <>
                                            <div className="form-group">

                                                <label>
                                                    Group Name
                                                    <span className="required"></span>
                                                </label>

                                               <input
                                                    type="text"
                                                    value={obj.group_name}
                                                    onChange={(e) =>
                                                        handleObjectChange(
                                                            obj.id,
                                                            "group_name",
                                                            e.target.value
                                                        )
                                                    }
                                                />

                                            </div>

                                            <div className="form-group">

                                                <label>
                                                    Email
                                                    <span className="required"></span>
                                                </label>

                                                <input
                                                    type="text"
                                                    value={obj.email}
                                                    onChange={(e) =>
                                                        handleObjectChange(
                                                            obj.id,
                                                            "email",
                                                            e.target.value
                                                        )
                                                    }
                                                />

                                            </div>
                                        </>
                                    )
                                }
                                {
                                    obj.objectType === "COMPUTER" && (

                                        <div className="form-group">

                                            <label>
                                                Computer Name
                                                <span className="required">*</span>
                                            </label>

                                            <input
                                                type="text"
                                                value={obj.computer_name}
                                                onChange={(e) =>
                                                    handleObjectChange(
                                                        obj.id,
                                                        "computer_name",
                                                        e.target.value
                                                    )
                                                }
                                            />

                                        </div>

                                    )
                                }
                                {
                                    obj.objectType === "CREATE_NEW_USER" && (
                                        <>
                                            <div className="form-group">
                                                <label>
                                                    Username
                                                    <span className="required">*</span>
                                                </label>

                                                <input
                                                    type="text"
                                                    value={obj.username}
                                                    onChange={(e) =>
                                                        handleObjectChange(
                                                            obj.id,
                                                            "username",
                                                            e.target.value
                                                        )
                                                    }
                                                />
                                            </div>

                                            <div className="form-group">
                                                <label>
                                                    Email
                                                    <span className="required">*</span>
                                                </label>

                                                <input
                                                    type="text"
                                                    value={obj.email}
                                                    onChange={(e) =>
                                                        handleObjectChange(
                                                            obj.id,
                                                            "email",
                                                            e.target.value
                                                        )
                                                    }
                                                />
                                            </div>
                                        </>
                                    )
                                }
                                {
                                    obj.objectType === "CREATE_NEW_GROUP" && (
                                        <div className="form-group">
                                            <label>
                                                Group Name
                                                <span className="required">*</span>
                                            </label>

                                            <input
                                                type="text"
                                                value={obj.group_name}
                                                onChange={(e) =>
                                                    handleObjectChange(
                                                        obj.id,
                                                        "group_name",
                                                        e.target.value
                                                    )
                                                }
                                            />
                                        </div>
                                    )
                                }








                            </div>

                        ))
                    }

                </div>







            </div>

        </div>

    );



}