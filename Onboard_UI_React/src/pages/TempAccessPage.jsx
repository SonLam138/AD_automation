import {
    useMemo,
    useState,
} from "react";

import "./TempAccessPage.css";
import {executeTempAccess, tempResolveObject} from "../services/adToolApi";

const TEMP_ACCESS_TYPE = {
    COMPUTER: "computer",
    USER: "user",
};

const ORIGINAL_VALUE =
    "__ORIGINAL_VALUE__";


const INITIAL_FORM = {
    targetIdentity: "",

    startDate: "",

    step01Value: "",

    step02Value: "",

    step02Mode: "ORIGINAL_VALUE",

    step02ExecuteAt: "",
};


export default function TempAccessPage() {

    const [
        selectedType,
        setSelectedType,
    ] = useState(null);

    const [
        formData,
        setFormData,
    ] = useState(
        INITIAL_FORM
    );

    const [
        validationErrors,
        setValidationErrors,
    ] = useState([]);

    const [
        validationPassed,
        setValidationPassed,
    ] = useState(false);

    const [
        isExecuting,
        setIsExecuting,
    ] = useState(false);

    const [
        executeResult,
        setExecuteResult,
    ] = useState(null);

    const [
        resolvingStepId,
        setResolvingStepId,
    ] = useState(null);


    const [
        resolvedSteps,
        setResolvedSteps,
    ] = useState({
        STEP_01: false,
        STEP_02: false,
    });


    const [
        resolveError,
        setResolveError,
    ] = useState(null);


    const [
        resolveOptions,
        setResolveOptions,
    ] = useState([]);


    const [
        selectingStepId,
        setSelectingStepId,
    ] = useState(null);

    const typeConfiguration = useMemo(
        () => {

            if (
                selectedType
                ===
                TEMP_ACCESS_TYPE.COMPUTER
            ) {
                return {
                    title:
                        "Temporary Access for Computer",

                    identityLabel:
                        "Computer Name",

                    identityPlaceholder:
                        "Ví dụ: Client-01",

                    step01Title:
                        "STEP_01",

                    step01Description:
                        "Move computer to the first target OU",

                    step02Title:
                        "STEP_02",

                    step02Description:
                        "Move computer to the second target OU",

                    valueLabel:
                        "Target OU",

                    valuePlaceholder:
                        (
                            "OU=HO,"
                            + "DC=automate,"
                            + "DC=com,"
                            + "DC=vn"
                        ),

                    requestType:
                        "temp_access_computer",

                    context:
                        "TEMP_ACCESS_COMPUTER",

                    identityField:
                        "computer_name",

                    objectType:
                        "OU",

                    parameterName:
                        "target_ou",
                };
            }


            if (
                selectedType
                ===
                TEMP_ACCESS_TYPE.USER
            ) {
                return {
                    title:
                        "Temporary Access for User",

                    identityLabel:
                        "Email",

                    identityPlaceholder:
                        "Ví dụ: UserA@domain.com.vn",

                    step01Title:
                        "STEP_01",

                    step01Description:
                        "Add user to group to grant permission",

                    step02Title:
                        "STEP_02",

                    step02Description:
                        "Remove user from the same group",

                    valueLabel:
                        "Target Group",

                    valuePlaceholder:
                        "Ví dụ: VPN_USERS",

                    requestType:
                        "temp_access_user",

                    context:
                        "TEMP_ACCESS_USER",

                    identityField:
                        "email",

                    objectType:
                        "GROUP",

                    parameterName:
                        "target_group",
                };
            }

            return null;
        },
        [
            selectedType,
        ]
    );


    function resetForm() {

        setFormData({
        ...INITIAL_FORM,
        step02Value:
        ORIGINAL_VALUE,
        });

        setValidationErrors([]);

        setValidationPassed(false);

        setExecuteResult(null);

        setIsExecuting(false);

        setResolvedSteps({
            STEP_01: false,
            STEP_02: false,
        });

        setResolvingStepId(
            null
        );

        setResolveOptions([]);

        setSelectingStepId(
            null
        );

        setResolveError(
            null
        );
    }
    function handleSelectResolvedObject(
        option
    ) {

        if (!selectingStepId) {
            return;
        }


        const fieldName = (
            selectingStepId
            ===
            "STEP_01"

                ? "step01Value"

                : "step02Value"
        );


        setFormData(
            current => ({
                ...current,

                [fieldName]:
                    option
                        .distinguished_name,
            })
        );


        setResolvedSteps(
            current => ({
                ...current,

                [selectingStepId]:
                    true,
            })
        );


        setResolveOptions([]);

        setSelectingStepId(
            null
        );

        setResolveError(
            null
        );

        setValidationPassed(
            false
        );
    }

    async function handleGetDn(
        stepId,
        fieldName
    ) {
        const keyword = (
            formData[fieldName]
            ?.trim()
        );

        if (!keyword) {
            setResolveError(
                `Chưa nhập giá trị cho ${stepId}.`
            );

            return;
        }

        setResolvingStepId(
            stepId
        );

        setResolveError(
            null
        );

        setResolveOptions([]);

        setSelectingStepId(
            null
        );

        try {
            const result = (
                await tempResolveObject(
                    typeConfiguration.objectType,
                    keyword
                )
            );

            if (
                result.resolved
                &&
                result.distinguished_name
            ) {
                setFormData(
                    current => ({
                        ...current,

                        [fieldName]:
                            result.distinguished_name,
                    })
                );

                setResolvedSteps(
                    current => ({
                        ...current,

                        [stepId]:
                            true,
                    })
                );

                setValidationPassed(
                    false
                );

                return;
            }

            if (
                result.multiple
                &&
                Array.isArray(
                    result.results
                )
                &&
                result.results.length > 0
            ) {
                setResolveOptions(
                    result.results
                );

                setSelectingStepId(
                    stepId
                );

                return;
            }

            setResolveError(
                result.message
                ||
                `Không tìm thấy OU cho ${stepId}.`
            );

            setResolvedSteps(
                current => ({
                    ...current,

                    [stepId]: false,
                })
            );

        } catch (error) {
            const backendDetail = (
                error
                    ?.response
                    ?.data
                    ?.detail
            );

            let errorMessage = (
                error.message
                ||
                "Không thể resolve DN."
            );

            if (
                typeof backendDetail
                ===
                "string"
            ) {
                errorMessage =
                    backendDetail;
            }

            if (
                Array.isArray(
                    backendDetail
                )
            ) {
                errorMessage = (
                    backendDetail
                        .map(
                            item =>
                                item.msg
                        )
                        .join(", ")
                );
            }

            setResolveError(
                errorMessage
            );

            setResolvedSteps(
                current => ({
                    ...current,

                    [stepId]: false,
                })
            );

        } finally {
            setResolvingStepId(
                null
            );
        }
    }


    function selectType(
        type
    ) {

        setSelectedType(
            type
        );

        resetForm();
    }


    function updateField(
        fieldName,
        value
    ) {

        setFormData(
            current => ({
                ...current,

                [fieldName]:
                    value,
            })
        );


        if (
            fieldName
            ===
            "step01Value"
        ) {
            setResolvedSteps(
                current => ({
                    ...current,

                    STEP_01:
                        false,
                })
            );
        }


        if (
            fieldName
            ===
            "step02Value"
        ) {
            setResolvedSteps(
                current => ({
                    ...current,

                    STEP_02:
                        false,
                })
            );
        }


        setValidationPassed(
            false
        );

        setValidationErrors([]);

        setExecuteResult(
            null
        );

        setResolveError(
            null
        );
    }


    function buildPayload() {

        if (!typeConfiguration) {
            return null;
        }

        return {
            request_type:
                typeConfiguration
                    .requestType,

            context:
                typeConfiguration
                    .context,

            [
                typeConfiguration
                    .identityField
            ]:
                formData
                    .targetIdentity
                    .trim(),

            start_date:
                formData.startDate,

            step_execute_times: [
                {
                    step_id:
                        "STEP_02",

                    execute_at:
                        formData.step02ExecuteAt,
                },
            ],

            step_new_values: [
                {
                    step_id:
                        "STEP_01",

                    parameter_name:
                        typeConfiguration
                            .parameterName,

                    new_value:
                        formData
                            .step01Value
                            .trim(),
                },

                {
                    step_id:
                        "STEP_02",

                    parameter_name:
                        typeConfiguration
                            .parameterName,

                    new_value:
                        formData
                            .step02Value
                            .trim(),
                },
            ],
        };
    }


    function validateForm() {

        const errors = [];

        if (!selectedType) {
            errors.push(
                "Chưa chọn loại Temporary Access."
            );
        }

        if (
            !formData
                .targetIdentity
                .trim()
        ) {
            errors.push(
                selectedType
                ===
                TEMP_ACCESS_TYPE.COMPUTER
                    ? "Computer Name là bắt buộc."
                    : "SAM Account Name là bắt buộc."
            );
        }

        if (!formData.startDate) {
            errors.push(
                "Workflow Start Date là bắt buộc."
            );
        }
        console.log(
            "step01Value",
            formData.step01Value
        );

        console.log(
            "resolvedSteps",
            resolvedSteps
        );

        if (
            !formData
                .step01Value
                .trim()
        ) {
            errors.push(
                "New Value của STEP_01 là bắt buộc."
            );
        }

        const requiresStep02Value =
            formData.step02Value
            !==
            ORIGINAL_VALUE;

        if (
            requiresStep02Value
            &&
            !formData
                .step02Value
                .trim()
        ) {
            errors.push(
                "Target Value của STEP_02 là bắt buộc."
            );
        }

        if (
            !formData
                .step02ExecuteAt
        ) {
            errors.push(
                "Execute Time của STEP_02 là bắt buộc."
            );
        }


        const startDate = (
            new Date(
                formData.startDate
            )
        );

        const step02Date = (
            new Date(
                formData
                    .step02ExecuteAt
            )
        );


        if (
            formData.startDate
            &&
            Number.isNaN(
                startDate.getTime()
            )
        ) {
            errors.push(
                "Workflow Start Date không hợp lệ."
            );
        }


        if (
            formData.step02ExecuteAt
            &&
            Number.isNaN(
                step02Date.getTime()
            )
        ) {
            errors.push(
                "Execute Time của STEP_02 không hợp lệ."
            );
        }


        if (
            !Number.isNaN(
                startDate.getTime()
            )
            &&
            !Number.isNaN(
                step02Date.getTime()
            )
            &&
            step02Date
            <=
            startDate
        ) {
            errors.push(
                (
                    "Execute Time của STEP_02 "
                    + "phải sau Workflow Start Date."
                )
            );
        }
        if (
            selectedType
            ===
            TEMP_ACCESS_TYPE.COMPUTER
        ) {

            if (
                !resolvedSteps.STEP_01
            ) {
                errors.push(
                    (
                        "STEP_01 Target OU "
                        + "chưa được Get DN."
                    )
                );
            }


            const requiresResolvedStep02 = (
                formData.step02Mode
                ===
                "REVOKE_OU"
            );

            if (
                requiresResolvedStep02
                &&
                !resolvedSteps.STEP_02
            ) {
                errors.push(
                    (
                        "STEP_02 Revoke OU "
                        + "chưa được Get DN."
                    )
                );
            }
        }


        const payload = (
            buildPayload()
        );


        if (
            payload
            &&
            payload
                .step_execute_times
                .some(
                    item =>
                        !item.execute_at
                )
        ) {
            errors.push(
                "Không thể chuẩn hóa thời gian chạy step."
            );
        }


        setValidationErrors(
            errors
        );

        setValidationPassed(
            errors.length === 0
        );

        setExecuteResult(null);


        if (
            errors.length === 0
        ) {
            console.log(
                "TEMP ACCESS PAYLOAD"
            );

            console.log(
                payload
            );
        }
    }


    async function executeWorkflow() {

        if (
            !validationPassed
        ) {
            return;
        }

        const payload = (
            buildPayload()
        );

        setIsExecuting(true);

        setExecuteResult(null);


        try {

            const response =
                await executeTempAccess(
                    payload
                );

            setExecuteResult({
                success: true,

                message:
                    "Workflow đã được tạo thành công.",

                data: response,
            });

        }
        catch (error) {

            setExecuteResult({
                success: false,

                message:
                    error?.response?.data?.detail
                    ||
                    error.message,
            });
        }
    }


    return (

        <div className="temp-access-page">

            <div className="temp-access-card">

                <div className="temp-access-header">

                    <div>

                        <span className="temp-access-eyebrow">
                            Workflow Automation Engine
                        </span>

                        <h2>
                            Temporary Access
                        </h2>

                        <p>
                            Chọn loại đối tượng và cấu hình
                            giá trị cùng lịch chạy cho từng
                            workflow step.
                        </p>

                    </div>

                </div>


                <div className="temp-access-type-grid">

                    <button
                        type="button"

                        className={
                            (
                                "temp-access-type-box "
                                +
                                (
                                    selectedType
                                    ===
                                    TEMP_ACCESS_TYPE.COMPUTER

                                    ? "active"

                                    : ""
                                )
                            )
                        }

                        onClick={() =>
                            selectType(
                                TEMP_ACCESS_TYPE.COMPUTER
                            )
                        }
                    >

                        <span className="type-icon">
                            💻
                        </span>

                        <strong>
                            Temporary Access
                            for Computer
                        </strong>

                        <small>
                            Move computer through
                            target OUs by workflow step.
                        </small>

                    </button>


                    <button
                        type="button"

                        className={
                            (
                                "temp-access-type-box "
                                +
                                (
                                    selectedType
                                    ===
                                    TEMP_ACCESS_TYPE.USER

                                    ? "active"

                                    : ""
                                )
                            )
                        }

                        onClick={() =>
                            selectType(
                                TEMP_ACCESS_TYPE.USER
                            )
                        }
                    >

                        <span className="type-icon">
                            👤
                        </span>

                        <strong>
                            Temporary Access
                            for User
                        </strong>

                        <small>
                            Apply group permissions
                            by workflow step.
                        </small>

                    </button>

                </div>


                {
                    typeConfiguration
                    &&
                    (

                        <div className="temp-access-form">

                            <div className="form-section-title">

                                <div>

                                    <span>
                                        Selected Workflow
                                    </span>

                                    <h3>
                                        {
                                            typeConfiguration
                                                .title
                                        }
                                    </h3>

                                </div>

                                <button
                                    type="button"

                                    className="reset-button"

                                    onClick={
                                        resetForm
                                    }
                                >
                                    Reset
                                </button>

                            </div>


                            <div className="form-grid">

                                <label className="form-field">

                                    <span>
                                        {
                                            typeConfiguration
                                                .identityLabel
                                        }
                                    </span>

                                    <input
                                        type="text"

                                        value={
                                            formData
                                                .targetIdentity
                                        }

                                        placeholder={
                                            typeConfiguration
                                                .identityPlaceholder
                                        }

                                        onChange={
                                            event =>
                                                updateField(
                                                    "targetIdentity",
                                                    event.target.value
                                                )
                                        }
                                    />

                                </label>


                                <label className="form-field">

                                    <span>
                                        Workflow Start Date
                                    </span>

                                    <input
                                        type="datetime-local"

                                        value={
                                            formData
                                                .startDate
                                        }

                                        onChange={
                                            event =>
                                                updateField(
                                                    "startDate",
                                                    event.target.value
                                                )
                                        }
                                    />

                                    <small>
                                        STEP_01 chạy cùng thời
                                        điểm bắt đầu workflow.
                                    </small>

                                </label>

                            </div>


                            <div className="workflow-step-card">

                                <div className="step-header">

                                    <div>

                                        <span className="step-id">
                                            {
                                                typeConfiguration
                                                    .step01Title
                                            }
                                        </span>

                                        <h4>
                                            {
                                                typeConfiguration
                                                    .step01Description
                                            }
                                        </h4>

                                    </div>

                                    <span className="step-time-badge">
                                        Workflow Start
                                    </span>

                                </div>


                                <div className="form-field">

                                    <span>
                                        {
                                            typeConfiguration
                                                .valueLabel
                                        }
                                    </span>

                                    <div className="resolve-input-row">

                                        <input
                                            type="text"
                                            value={
                                                formData
                                                    .step01Value
                                            }
                                            placeholder={
                                                typeConfiguration
                                                    .valuePlaceholder
                                            }
                                            onChange={
                                                event =>
                                                    updateField(
                                                        "step01Value",
                                                        event.target.value
                                                    )
                                            }
                                        />

                                        <button
                                            type="button"
                                            className="get-dn-button"
                                            disabled={
                                                resolvingStepId
                                                ===
                                                "STEP_01"
                                            }
                                            onClick={() =>
                                                handleGetDn(
                                                    "STEP_01",
                                                    "step01Value"
                                                )
                                            }
                                        >
                                            {
                                                resolvingStepId
                                                ===
                                                "STEP_01"
                                                    ? "Resolving..."
                                                    : "Get DN"
                                            }
                                        </button>

                                    </div>

                                    {
                                        resolvedSteps.STEP_01
                                        &&
                                        (
                                            <small
                                                className="
                                                    resolved-label
                                                "
                                            >
                                                ✓ DN resolved
                                            </small>
                                        )
                                    }

                                </div>

                            </div>


                            <div className="workflow-step-card">

                                <div className="step-header">

                                    <div>

                                        <span className="step-id">
                                            {
                                                typeConfiguration
                                                    .step02Title
                                            }
                                        </span>

                                        <h4>
                                            {
                                                typeConfiguration
                                                    .step02Description
                                            }
                                        </h4>

                                    </div>

                                    <span className="step-time-badge custom">
                                        UI Custom
                                    </span>

                                </div>


                                <div className="form-grid">

                                    <div className="form-field">

                                        {
                                            selectedType
                                            ===
                                            TEMP_ACCESS_TYPE.USER
                                            ? (
                                                <div className="same-group-card">

                                                    <span className="same-group-label">
                                                        Group to be removed
                                                    </span>

                                                    <strong className="same-group-value">
                                                        {
                                                            formData.step01Value
                                                            ||
                                                            "Chưa chọn Target Group tại STEP_01"
                                                        }
                                                    </strong>

                                                    <small>
                                                        STEP_02 sẽ tự động remove user
                                                        khỏi đúng Group đã được add tại
                                                        STEP_01.
                                                    </small>

                                                </div>
                                            )
                                            : (
                                                <>
                                                    <div className="step02-mode-options">

                                                        <label className="mode-option">

                                                            <input
                                                                type="radio"
                                                                name="step02Mode"
                                                                value="ORIGINAL_VALUE"
                                                                checked={
                                                                    formData.step02Mode
                                                                    ===
                                                                    "ORIGINAL_VALUE"
                                                                }
                                                                onChange={() => {

                                                                    updateField(
                                                                        "step02Mode",
                                                                        "ORIGINAL_VALUE"
                                                                    );

                                                                    updateField(
                                                                        "step02Value",
                                                                        ORIGINAL_VALUE
                                                                    );

                                                                    setResolvedSteps(
                                                                        current => ({
                                                                            ...current,
                                                                            STEP_02: true,
                                                                        })
                                                                    );
                                                                }}
                                                            />

                                                            <div>
                                                                <strong>
                                                                    Return to Original OU
                                                                </strong>

                                                                <small>
                                                                    Đưa Computer về OU ban đầu
                                                                    sau khi hết thời hạn.
                                                                </small>
                                                            </div>

                                                        </label>

                                                        <label className="mode-option">

                                                            <input
                                                                type="radio"
                                                                name="step02Mode"
                                                                value="REVOKE_OU"
                                                                checked={
                                                                    formData.step02Mode
                                                                    ===
                                                                    "REVOKE_OU"
                                                                }
                                                                onChange={() => {

                                                                    updateField(
                                                                        "step02Mode",
                                                                        "REVOKE_OU"
                                                                    );

                                                                    updateField(
                                                                        "step02Value",
                                                                        ""
                                                                    );

                                                                    setResolvedSteps(
                                                                        current => ({
                                                                            ...current,
                                                                            STEP_02: false,
                                                                        })
                                                                    );
                                                                }}
                                                            />

                                                            <div>
                                                                <strong>
                                                                    Move to Revoke OU
                                                                </strong>

                                                                <small>
                                                                    Chuyển Computer sang OU
                                                                    thu hồi quyền được chỉ định.
                                                                </small>
                                                            </div>

                                                        </label>

                                                    </div>

                                                    {
                                                        formData.step02Mode
                                                        ===
                                                        "REVOKE_OU"
                                                        ? (
                                                            <>
                                                                <span>
                                                                    {
                                                                        typeConfiguration
                                                                            .valueLabel
                                                                    }
                                                                </span>

                                                                <div className="resolve-input-row">

                                                                    <input
                                                                        type="text"
                                                                        value={
                                                                            formData.step02Value
                                                                        }
                                                                        placeholder={
                                                                            typeConfiguration
                                                                                .valuePlaceholder
                                                                        }
                                                                        onChange={
                                                                            event =>
                                                                                updateField(
                                                                                    "step02Value",
                                                                                    event.target.value
                                                                                )
                                                                        }
                                                                    />

                                                                    <button
                                                                        type="button"
                                                                        className="get-dn-button"
                                                                        disabled={
                                                                            resolvingStepId
                                                                            ===
                                                                            "STEP_02"
                                                                        }
                                                                        onClick={() =>
                                                                            handleGetDn(
                                                                                "STEP_02",
                                                                                "step02Value"
                                                                            )
                                                                        }
                                                                    >
                                                                        {
                                                                            resolvingStepId
                                                                            ===
                                                                            "STEP_02"
                                                                                ? "Resolving..."
                                                                                : "Get DN"
                                                                        }
                                                                    </button>

                                                                </div>

                                                                {
                                                                    resolvedSteps.STEP_02
                                                                    &&
                                                                    (
                                                                        <small className="resolved-label">
                                                                            ✓ DN resolved
                                                                        </small>
                                                                    )
                                                                }
                                                            </>
                                                        )
                                                        : (
                                                            <div className="original-ou-message">
                                                                Original OU sẽ được lấy tự động
                                                                từ Computer đã resolve trong adapter.
                                                            </div>
                                                        )
                                                    }
                                                </>
                                            )
                                        }

                                    </div>


                                    <label className="form-field">

                                        <span>
                                            Execute Time
                                        </span>

                                        <input
                                            type="datetime-local"

                                            value={
                                                formData
                                                    .step02ExecuteAt
                                            }

                                            onChange={
                                                event =>
                                                    updateField(
                                                        "step02ExecuteAt",
                                                        event.target.value
                                                    )
                                            }
                                        />

                                    </label>

                                </div>

                            </div>

                            {
                                resolveError
                                &&
                                (
                                    <div className="resolve-message error">

                                        {resolveError}

                                    </div>
                                )
                            }

                            {
                                selectingStepId
                                &&
                                resolveOptions.length
                                >
                                0
                                &&
                                (

                                    <div className="resolve-selection-panel">

                                        <div className="resolve-selection-header">

                                            <div>

                                                <strong>
                                                    Select resolved object
                                                </strong>

                                                <span>
                                                    {
                                                        selectingStepId
                                                    }
                                                </span>

                                            </div>


                                            <button
                                                type="button"

                                                className="resolve-close-button"

                                                onClick={() => {

                                                    setResolveOptions([]);

                                                    setSelectingStepId(
                                                        null
                                                    );

                                                }}
                                            >
                                                Close
                                            </button>

                                        </div>


                                        <div className="resolve-option-list">

                                            {
                                                resolveOptions.map(
                                                    option => (

                                                        <button
                                                            type="button"

                                                            className="resolve-option"

                                                            key={
                                                                option
                                                                    .distinguished_name
                                                            }

                                                            onClick={() =>
                                                                handleSelectResolvedObject(
                                                                    option
                                                                )
                                                            }
                                                        >

                                                            <strong>
                                                                {
                                                                    option.name
                                                                    ||
                                                                    "OU"
                                                                }
                                                            </strong>

                                                            <span>
                                                                {
                                                                    option
                                                                        .distinguished_name
                                                                }
                                                            </span>

                                                        </button>

                                                    )
                                                )
                                            }

                                        </div>

                                    </div>

                                )
                            }


                            {
                                validationErrors.length
                                >
                                0
                                &&
                                (

                                    <div className="validation-panel error">

                                        <strong>
                                            Validation failed
                                        </strong>

                                        <ul>

                                            {
                                                validationErrors.map(
                                                    error => (

                                                        <li key={error}>
                                                            {error}
                                                        </li>

                                                    )
                                                )
                                            }

                                        </ul>

                                    </div>

                                )
                            }


                            {
                                validationPassed
                                &&
                                (

                                    <div className="validation-panel success">

                                        <strong>
                                            Validation passed
                                        </strong>

                                        <span>
                                            Payload đã sẵn sàng
                                            để chạy workflow.
                                        </span>

                                    </div>

                                )
                            }


                            {
                                executeResult
                                &&
                                (

                                    <div
                                        className={
                                            (
                                                "execution-result "
                                                +
                                                (
                                                    executeResult.success

                                                    ? "success"

                                                    : "error"
                                                )
                                            )
                                        }
                                    >
                                        {
                                            executeResult.message
                                        }
                                    </div>

                                )
                            }


                            <div className="form-actions">

                                <button
                                    type="button"

                                    className="validate-button"

                                    disabled={
                                        isExecuting
                                    }

                                    onClick={
                                        validateForm
                                    }
                                >
                                    Validate
                                </button>


                                <button
                                    type="button"

                                    className="execute-button"

                                    disabled={
                                        !validationPassed
                                        ||
                                        isExecuting
                                    }

                                    onClick={
                                        executeWorkflow
                                    }
                                >
                                    {
                                        isExecuting
                                            ? "Executing..."
                                            : "Execute Workflow"
                                    }
                                </button>

                            </div>

                        </div>

                    )
                }

            </div>

        </div>
    );
}