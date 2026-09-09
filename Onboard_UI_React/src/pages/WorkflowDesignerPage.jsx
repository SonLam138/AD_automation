import "./WorkflowDesignerPage.css";
import {ACTION_CATALOG} from "./actionCatalog";

import {useState} from "react";
import {tempResolveObject} from "../services/adToolApi";

import {useLocation} from "react-router-dom";
import axiosClient from "../api/axiosClient";
import { useNavigate } from "react-router-dom";

export default function WorkflowDesignerPage() {

    const location = useLocation();
    const navigate = useNavigate();
    const [
        resolveOptions,
        setResolveOptions
    ] = useState([]);

    const [
        resolveContext,
        setResolveContext
    ] = useState(null);

    const [steps, setSteps] = useState([]);
    const [saved, setSaved] =
        useState(false);

    const [executed, setExecuted] =
        useState(false);

    const workflowInfo =
        location.state?.workflowInfo || {};

    const objects =
        location.state?.objects || [];

    const handleAddStep = () => {

        setSteps(prev => [
            ...prev,
            {
                id: Date.now(),

                objectRef: "",

                action: "",

                executeTime: "",

                parameters: {},

                parameterStatus: "EDITING"
            }
        ]);
    };

    const handleStepChange = (
        id,
        field,
        value
    ) => {

        setSteps(prev => {

            const updated = prev.map(step => {

                if (step.id !== id) {
                    return step;
                }

                if (field === "objectRef") {

                    return {
                        ...step,

                        objectRef: value,

                        action: "",

                        parameters: {},

                        parameterStatus:
                            "EDITING"
                    };
                }

                if (field === "action") {

                    return {
                        ...step,

                        action: value,

                        parameters: {},

                        parameterStatus:
                            "EDITING"
                    };
                }

                return {
                    ...step,
                    [field]: value
                };
            });

            return updated;
        });

    };

    const handleParameterChange = (
        stepId,
        field,
        value
    ) => {

        setSteps(prev =>
            prev.map(step =>
                step.id === stepId
                    ? {
                        ...step,
                        parameters: {
                            ...step.parameters,
                            [field]: value
                        }
                    }
                    : step
            )
        );

    };

    const handleConfirmParameters = (
        stepId
    ) => {

        const step = steps.find(
            s => s.id === stepId
        );

        if (!step) {
            return;
        }

        const selectedObject =
            objects.find(
                obj =>
                    obj.alias === step.objectRef
            );

        if (
            step.action === "CREATE"
            &&
            selectedObject?.objectType ===
                "CREATE_NEW_USER"
        )
        {
            if (
                !step.parameters.givenName?.trim()
            ) {
                alert(
                    "Given Name is required"
                );
                return;
            }

            if (
                !step.parameters.surname?.trim()
            ) {
                alert(
                    "Surname is required"
                );
                return;
            }

            if (
                !step.parameters.displayName?.trim()
            ) {
                alert(
                    "Display Name is required"
                );
                return;
            }

            if (
                !step.parameters.targetOu?.trim()
            ) {
                alert(
                    "Target OU is required"
                );
                return;
            }
        }
        if (
            step.action === "CREATE"
            &&
            selectedObject?.objectType ===
                "CREATE_NEW_GROUP"
        )
        {
            if (
                !step.parameters.groupName?.trim()
            ) {
                alert(
                    "Group Name is required"
                );
                return;
            }

            if (
                !step.parameters.displayName?.trim()
            ) {
                alert(
                    "Display Name is required"
                );
                return;
            }

            if (
                !step.parameters.targetOu?.trim()
            ) {
                alert(
                    "Target OU is required"
                );
                return;
            }
        }
        if (
            step.action === "MOVE"
        )
        {
            if (
                !step.parameters.targetOu?.trim()
            ) {
                alert(
                    "Target OU is required"
                );
                return;
            }
        }
        if (
            step.action === "ADD_GROUP"
        )
        {
            if (
                !step.parameters.targetGroup?.trim()
            ) {
                alert(
                    "Target Group is required"
                );
                return;
            }
        }
        if (
            step.action === "REMOVE_GROUP"
        )
        {
            if (
                !step.parameters.targetGroup?.trim()
            ) {
                alert(
                    "Target Group is required"
                );
                return;
            }
        }

        setSteps(prev =>
            prev.map(step =>
                step.id === stepId
                    ? {
                        ...step,
                        parameterStatus:
                            "CONFIRMED"
                    }
                    : step
            )
        );

        

        

    };

    const handleResetParameters = (
        stepId
    ) => {

        setSteps(prev =>
            prev.map(step =>
                step.id === stepId
                    ? {
                        ...step,
                        parameters: {},
                        parameterStatus:
                            "EDITING"
                    }
                    : step
            )
        );

    };

    const handleRemoveStep = (
        stepId
    ) => {

        setSteps(prev =>
            prev.filter(
                step =>
                    step.id !== stepId
            )
        );

    };

    const handleReviewAndSave = async () => {

    const errors = [];
    // validate workflow theo 5 tầng
    // Tầng 1
    if (
        !workflowInfo.workflowName?.trim()
    ) {

        errors.push(
            "Workflow Name is required"
        );

    }

    if (objects.length === 0) {

        errors.push(
            "At least one object is required"
        );

    }

    if (steps.length === 0) {

        errors.push(
            "At least one workflow step is required"
        );

    }

    // Tầng 2
    steps.forEach((step, index) => {
        const selectedObject =
            objects.find(
            obj =>
            obj.alias === step.objectRef
            );

        if (!step.objectRef) {

            errors.push(
                `Step ${index + 1}: Object is required`
            );
        }

        if (!step.action) {

            errors.push(
                `Step ${index + 1}: Action is required`
            );
        }
        if (
            step.action === "CREATE"
            &&
            selectedObject?.objectType ===
                "CREATE_NEW_USER"
        )
        {
            if (!step.parameters.givenName) {

                errors.push(
                    `Step ${index + 1}: Given Name is required`
                );
            }

            if (!step.parameters.surname) {

                errors.push(
                    `Step ${index + 1}: Surname is required`
                );
            }

            if (!step.parameters.displayName) {

                errors.push(
                    `Step ${index + 1}: Display Name is required`
                );
            }

            if (!step.parameters.targetOu) {

                errors.push(
                    `Step ${index + 1}: Target OU is required`
                );
            }
        }
        if (
            step.action === "CREATE"
            &&
            selectedObject?.objectType ===
                "CREATE_NEW_GROUP"
        )
        {
            if (!step.parameters.groupName) {

                errors.push(
                    `Step ${index + 1}: Group Name is required`
                );
            }

            if (!step.parameters.displayName) {

                errors.push(
                    `Step ${index + 1}: Display Name is required`
                );
            }

            if (!step.parameters.targetOu) {

                errors.push(
                    `Step ${index + 1}: Target OU is required`
                );
            }
        }

        // Tầng 3: Validate action parameters
        if (
            step.action === "MOVE"
            &&
            !step.parameters.targetOu?.trim()
        ) {
            errors.push(
                `Step ${index + 1}: Target OU is required`
            );
        }

        if (
            step.action === "ADD_GROUP"
            &&
            !step.parameters.targetGroup?.trim()
        ) {
            errors.push(
                `Step ${index + 1}: Target Group is required`
            );
        }

        const actionsRequireConfirmation = [
            "CREATE",
            "MOVE",
            "ADD_GROUP",
            "REMOVE_GROUP"
        ];

        if (
            actionsRequireConfirmation.includes(
                step.action
            )
            &&
            step.parameterStatus !== "CONFIRMED"
        ) {
            errors.push(
                `Step ${index + 1}: Parameters must be confirmed`
            );
        }
        // Tầng 4: Validate Execute Time
        if (!step.executeTime) {

            errors.push(
                `Step ${index + 1}: Execute Time is required`
            );

        } else if (
            Number.isNaN(
                new Date(step.executeTime).getTime()
            )
        ) {

            errors.push(
                `Step ${index + 1}: Execute Time is invalid`
            );

        }

    });

    // Tàng 5
    for (
        let i = 1;
        i < steps.length;
        i++
    ) {

        const previousStep =
            steps[i - 1];

        const currentStep =
            steps[i];

        if (
            previousStep.executeTime
            &&
            currentStep.executeTime
            &&
            new Date(
                currentStep.executeTime
            ) <
            new Date(
                previousStep.executeTime
            )
        ) {

            errors.push(
                `Step ${i + 1}: Execute time must be greater than previous step`
            );

        }

    }


    if (errors.length > 0) {

        alert(
            errors.join("\n")
        );

        return;
    }
// Save


    try {

        const payload = {
            workflowInfo,
            objects,
            steps
        };

        const response =
            await axiosClient.post(
                "/api/workflow/custom-workflow/save",
                payload
            );

        console.log(
            "Save Result:",
            response.data
        );
        setSaved(true);

        alert(
            `Workflow saved successfully.\n` +
            `Generated ${response.data.templateCount} template(s).`
        );

    } catch (error) {

        console.error(
            "Save workflow failed:",
            error
        );

        alert(
            "Failed to save workflow."
        );
    }
    };

    const handleExecute = async () => {

        try {

            const payload = {
                workflowInfo,
                objects,
                steps
            };

            const response =
                await axiosClient.post(
                    "/api/workflow/custom-workflow/run",
                    payload
                );

            console.log(
                "Execute Result:",
                response.data
            );
            setExecuted(true);

            alert(
                `Workflow submitted successfully.\n` +
                `Created ${response.data.planCount} plan(s).`
            );

        } catch (error) {

            console.error(
                "Execute workflow failed:",
                error
            );

            alert(
                "Failed to execute workflow."
            );
        }
    };

    function getResolveObjectType(
        parameterName
    ) {

        switch (
            parameterName
        ) {

            case "targetOu":
                return "OU";

            case "targetGroup":
                return "GROUP";

            default:
                return null;
        }
    }

    async function handleResolveParameter(
        stepId,
        parameterName,
        currentValue
    ) {
        const objectType =
            getResolveObjectType(
                parameterName
            );

        if (!objectType) {
            return;
        }

        try {
            const response =
                await tempResolveObject(
                    objectType,
                    currentValue
                );

            const result =
                response?.data ?? response;

            console.log(
                "Resolve parameter result:",
                result
            );

            if (
                result.resolved
                &&
                result.distinguished_name
            ) {
                handleParameterChange(
                    stepId,
                    parameterName,
                    result.distinguished_name
                );

                return;
            }

            if (result.multiple) {
                setResolveOptions(
                    result.results || []
                );

                setResolveContext({
                    stepId,
                    parameterName
                });

                return;
            }

            alert(
                result.message
                || "Object not found"
            );
        }
        catch (error) {
            alert(
                error?.response?.data?.detail
                || error.message
            );
        }
    }

    function handleSelectResolvedObject(
        option
    ) {
        if (!resolveContext) {
            return;
        }

        handleParameterChange(
            resolveContext.stepId,
            resolveContext.parameterName,
            option.distinguished_name
        );

        setResolveOptions([]);
        setResolveContext(null);
    }

    function closeResolveOptions() {
        setResolveOptions([]);
        setResolveContext(null);
    }




    return (

        <div className="workflow-designer-page">

            <div className="workflow-designer-header">

                <div>

                    <h2>
                        Workflow Designer
                    </h2>

                    <p className="workflow-designer-subtitle">
                        Design and execute workflow steps.
                    </p>

                </div>

                <div className="designer-actions">

                    <button
                        className="save-btn"
                        onClick={handleReviewAndSave}
                        disabled={saved}
                    >
                        {saved
                            ? "Saved ✓"
                            : "Review & Save"}
                    </button>

                    <button
                        className="execute-btn"
                        onClick={handleExecute}
                        disabled={!saved || executed}
                    >
                        {executed
                            ? "Executed ✓"
                            : "Execute"}
                    </button>

                </div>

            </div>
            <div className="workflow-designer-layout">

                <div className="designer-sidebar">
                    <h3>
                         Objects
                    </h3>
                    <div className="object-count">

                        {objects.length} object(s)

                    </div>
                    {
                        objects.map(obj => (

                            <div
                                key={obj.id}
                                className="sidebar-object"
                            >

                                <strong>
                                    {obj.alias}
                                </strong>
                                <div>
                                    {obj.objectType}
                                </div>

                            </div>

                        ))
                    }


                </div>

                <div className="designer-main">

                    <div className="steps-header">

                        <h3>
                            Workflow Steps
                        </h3>

                        <button
                            type="button"
                            onClick={handleAddStep}
                        >
                            + Add Step
                        </button>

                    </div>
                    {
                        steps.map((step, index) => {

                            const selectedObject =
                                objects.find(
                                    obj =>
                                        obj.alias === step.objectRef
                                );
                                const availableActions =
                                    ACTION_CATALOG[
                                        selectedObject?.objectType
                                    ] || [];

                            return (

                                <div
                                    key={step.id}
                                    className="step-card"
                                >

                                <div className="step-header">

                                    <strong>
                                        Step {index + 1}
                                    </strong>

                                    <button
                                        type="button"
                                        onClick={() =>
                                            handleRemoveStep(
                                                step.id
                                            )
                                        }
                                    >
                                        Remove
                                    </button>

                                </div>


                                <div className="form-group">

                                    <label>
                                        Object
                                    </label>

                                    <select
                                        value={step.objectRef}
                                        disabled={
                                            step.parameterStatus ===
                                            "CONFIRMED"
                                        }
                                        onChange={(e) =>
                                            handleStepChange(
                                                step.id,
                                                "objectRef",
                                                e.target.value
                                            )
                                        }
                                    >
                                        <option value="">
                                            Select Object
                                        </option>

                                        {
                                            objects.map(obj => (

                                                <option
                                                    key={obj.id}
                                                    value={obj.alias}
                                                >
                                                    {obj.alias}
                                                </option>

                                            ))
                                        }

                                    </select>

                                </div>

                                <div className="form-group">

                                    <label>
                                        Action
                                    </label>

                                    <select
                                        value={step.action}
                                        disabled={
                                            !selectedObject
                                            ||
                                            step.parameterStatus ===
                                                "CONFIRMED"
                                        }
                                        onChange={(e) =>
                                            handleStepChange(
                                                step.id,
                                                "action",
                                                e.target.value
                                            )
                                        }
                                    >

                                        <option value="">
                                            {
                                                selectedObject
                                                    ? "Select Action"
                                                    : "Select Object First"
                                            }
                                        </option>

                                        {
                                            availableActions.map(
                                                action => (
                                                    <option
                                                        key={action}
                                                        value={action}
                                                    >
                                                        {action}
                                                    </option>
                                                )
                                            )
                                        }
                                    </select>

                                </div>

                                <div className="form-group">

                                    <label>
                                        Execute Time
                                    </label>

                                    <input
                                        type="datetime-local"
                                        value={step.executeTime}
                                        onChange={(e) =>
                                            handleStepChange(
                                                step.id,
                                                "executeTime",
                                                e.target.value
                                            )
                                        }
                                    />

                                </div>

                                <div className="action-parameters">

                                    <div className="parameter-header">

                                        <h4>
                                            Action Parameters
                                        </h4>

                                        <span
                                            className={
                                                step.parameterStatus === "CONFIRMED"
                                                    ? "parameter-status confirmed"
                                                    : "parameter-status editing"
                                            }
                                        >
                                            {
                                                step.parameterStatus === "CONFIRMED"
                                                    ? "CONFIRMED"
                                                    : "EDITING"
                                            }
                                        </span>

                                    </div>

                                    <div className="current-action">

                                        Current Action:
                                        <strong>
                                            {step.action || "NONE"}
                                        </strong>

                                    </div>
                                    {
                                        step.action === "CREATE"
                                        &&
                                        selectedObject?.objectType === "CREATE_NEW_USER"
                                        &&
                                        (

                                            <div className="parameter-group">

                                                <div className="form-group">

                                                    <label>
                                                        Given Name
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.givenName
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "givenName",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>

                                                <div className="form-group">

                                                    <label>
                                                        Surname
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.surname
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "surname",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>
                                                <div className="form-group">

                                                    <label>
                                                        Display Name
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.displayName
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "displayName",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>
                                                <div className="form-group">

                                                    <label>
                                                        Target OU
                                                    </label>

                                                    <div className="parameter-input-row">

                                                        <input
                                                            type="text"
                                                            value={
                                                                step.parameters.targetOu
                                                                || ""
                                                            }
                                                            readOnly={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onChange={(e) =>
                                                                handleParameterChange(
                                                                    step.id,
                                                                    "targetOu",
                                                                    e.target.value
                                                                )
                                                            }
                                                        />

                                                        <button
                                                            type="button"
                                                            disabled={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onClick={() =>
                                                                handleResolveParameter(
                                                                    step.id,
                                                                    "targetOu",
                                                                    step.parameters.targetOu
                                                                )
                                                            }
                                                        >
                                                            Get DN
                                                        </button>

                                                    </div>

                                                </div>



                                            </div>

                                        )
                                    }

                                    {
                                        step.action === "CREATE"
                                        &&
                                        selectedObject?.objectType ===
                                            "CREATE_NEW_GROUP"
                                        &&
                                        (
                                            <div className="parameter-group">

                                                <div className="form-group">

                                                    <label>
                                                        Group Name
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.groupName
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "groupName",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>

                                                <div className="form-group">

                                                    <label>
                                                        Display Name
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.displayName
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "displayName",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>

                                                <div className="form-group">

                                                    <label>
                                                        Description
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.description
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "description",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>

                                                <div className="form-group">

                                                    <label>
                                                        Target OU
                                                    </label>

                                                    <div className="parameter-input-row">

                                                        <input
                                                            type="text"
                                                            value={
                                                                step.parameters.targetOu
                                                                || ""
                                                            }
                                                            readOnly={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onChange={(e) =>
                                                                handleParameterChange(
                                                                    step.id,
                                                                    "targetOu",
                                                                    e.target.value
                                                                )
                                                            }
                                                        />

                                                        <button
                                                            type="button"
                                                            disabled={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onClick={() =>
                                                                handleResolveParameter(
                                                                    step.id,
                                                                    "targetOu",
                                                                    step.parameters.targetOu
                                                                )
                                                            }
                                                        >
                                                            Get DN
                                                        </button>

                                                    </div>

                                                </div>

                                            </div>
                                        )
                                    }

                                    {
                                        step.action === "CREATE"
                                        &&
                                        selectedObject?.objectType === "COMPUTER"
                                        &&
                                        (

                                            <div className="parameter-group">

                                                <div className="form-group">

                                                    <label>
                                                        Target OU
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.targetOu
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "targetOu",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>

                                                <div className="form-group">

                                                    <label>
                                                        Description
                                                    </label>

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.description
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "description",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                </div>

                                            </div>

                                        )
                                    }
                                    {
                                        step.action === "MOVE"
                                        &&
                                        (
                                            <div className="form-group">

                                                <label>
                                                    Target OU
                                                </label>

                                                <div className="parameter-input-row">

                                                    <input
                                                        type="text"
                                                        value={
                                                            step.parameters.targetOu
                                                            || ""
                                                        }
                                                        readOnly={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onChange={(e) =>
                                                            handleParameterChange(
                                                                step.id,
                                                                "targetOu",
                                                                e.target.value
                                                            )
                                                        }
                                                    />

                                                    <button
                                                        type="button"
                                                        disabled={
                                                            step.parameterStatus ===
                                                            "CONFIRMED"
                                                        }
                                                        onClick={() =>
                                                            handleResolveParameter(
                                                                step.id,
                                                                "targetOu",
                                                                step.parameters.targetOu
                                                            )
                                                        }
                                                    >
                                                        Get DN
                                                    </button>

                                                </div>

                                            </div>
                                        )
                                    }
                                    {
                                        step.action === "ADD_GROUP"
                                        &&
                                        (
                                            <div className="parameter-group">

                                                <div className="form-group">

                                                    <label>
                                                        Target Group
                                                    </label>

                                                    <div className="parameter-input-row">

                                                        <input
                                                            type="text"
                                                            value={
                                                                step.parameters.targetGroup
                                                                || ""
                                                            }
                                                            readOnly={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onChange={(e) =>
                                                                handleParameterChange(
                                                                    step.id,
                                                                    "targetGroup",
                                                                    e.target.value
                                                                )
                                                            }
                                                        />

                                                        <button
                                                            type="button"
                                                            disabled={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onClick={() =>
                                                                handleResolveParameter(
                                                                    step.id,
                                                                    "targetGroup",
                                                                    step.parameters.targetGroup
                                                                )
                                                            }
                                                        >
                                                            Get DN
                                                        </button>

                                                    </div>

                                                </div>

                                            </div>
                                        )
                                    }
                                    {
                                        step.action === "REMOVE_GROUP"
                                        &&
                                        (
                                            <div className="parameter-group">

                                                <div className="form-group">

                                                    <label>
                                                        Target Group
                                                    </label>

                                                    <div className="parameter-input-row">

                                                        <input
                                                            type="text"
                                                            value={
                                                                step.parameters.targetGroup
                                                                || ""
                                                            }
                                                            readOnly={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onChange={(e) =>
                                                                handleParameterChange(
                                                                    step.id,
                                                                    "targetGroup",
                                                                    e.target.value
                                                                )
                                                            }
                                                        />

                                                        <button
                                                            type="button"
                                                            disabled={
                                                                step.parameterStatus ===
                                                                "CONFIRMED"
                                                            }
                                                            onClick={() =>
                                                                handleResolveParameter(
                                                                    step.id,
                                                                    "targetGroup",
                                                                    step.parameters.targetGroup
                                                                )
                                                            }
                                                        >
                                                            Get DN
                                                        </button>

                                                    </div>

                                                </div>

                                            </div>
                                        )
                                    }

                                    <div className="parameter-actions">

                                        <button
                                            type="button"
                                            className="confirm-btn"
                                            onClick={() =>
                                                handleConfirmParameters(
                                                    step.id
                                                )
                                            }
                                        >
                                            Confirm
                                        </button>

                                        <button
                                            type="button"
                                            className="reset-btn"
                                            onClick={() =>
                                                handleResetParameters(
                                                    step.id
                                                )
                                            }
                                        >
                                            Reset
                                        </button>

                                    </div>
                                    
                                </div>

                            </div>

                            );

                        })
                    }

                    {
                        resolveContext
                        &&
                        resolveOptions.length > 0
                        &&
                        (
                            <div className="resolve-selection-panel">
                                <div className="resolve-selection-header">
                                    <div>
                                        <strong>
                                            Select resolved object
                                        </strong>
                                        <span>
                                            Choose a DN to fill the parameter
                                        </span>
                                    </div>

                                    <button
                                        type="button"
                                        className="resolve-close-button"
                                        onClick={closeResolveOptions}
                                    >
                                        Close
                                    </button>
                                </div>

                                <div className="resolve-option-list">
                                    {
                                        resolveOptions.map(option => (
                                            <button
                                                type="button"
                                                className="resolve-option"
                                                key={option.distinguished_name}
                                                onClick={() =>
                                                    handleSelectResolvedObject(
                                                        option
                                                    )
                                                }
                                            >
                                                <strong>
                                                    {option.name || "Object"}
                                                </strong>
                                                <span>
                                                    {option.distinguished_name}
                                                </span>
                                            </button>
                                        ))
                                    }
                                </div>
                            </div>
                        )
                    }

                </div>

            </div>

        </div>

    );

}