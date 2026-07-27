import "./MultiSelector.css";


function MultiSelector({
    Data,
    onSelect
}) {
    const candidateObjects =
        Data?.candidate_objects || {};

    const selectedObjects =
        Data?.selected_objects || {};

    const objectEntries =
        Object.entries(candidateObjects);

    const getCandidateKey = (
        candidate,
        index
    ) => {
        return (
            candidate?.object_guid ||
            candidate?.objectGUID ||
            candidate?.id ||
            candidate?.distinguished_name ||
            candidate?.dn ||
            candidate?.sam_account_name ||
            candidate?.samaccountname ||
            candidate?.name ||
            `candidate-${index}`
        );
    };


    const getDisplayValue = (candidate) => {
        if (!candidate) {
            return "";
        }
        console.log(
            "DISPLAY",
            candidate.display_name,
            candidate.sam_account_name
        );

        return (
            candidate.displayName ||
            candidate.display_name ||
            candidate.name ||
            candidate.sam_account_name ||
            candidate.samaccountname ||
            candidate.cn ||
            candidate.distinguished_name ||
            candidate.dn ||
            JSON.stringify(candidate)
        );
    };


    const getSecondaryValue = (candidate) => {
        if (!candidate) {
            return "";
        }

        return (
            candidate.mail ||
            candidate.sam_account_name ||
            candidate.department ||
            ""
        );
    };


    const isSameCandidate = (
        left,
        right
    ) => {
        if (!left || !right) {
            return false;
        }

        const leftKey =
            left.object_guid ||
            left.objectGUID ||
            left.id ||
            left.distinguished_name ||
            left.dn ||
            left.sam_account_name ||
            left.samaccountname ||
            left.name;

        const rightKey =
            right.object_guid ||
            right.objectGUID ||
            right.id ||
            right.distinguished_name ||
            right.dn ||
            right.sam_account_name ||
            right.samaccountname ||
            right.name;

        return (
            leftKey &&
            rightKey &&
            leftKey === rightKey
        );
    };


    const handleSelect = (
        objectType,
        candidate
    ) => {
        if (!onSelect) {
            return;
        }

        onSelect(
            Data,
            objectType,
            candidate
        );
    };


    const requiredCount =
        objectEntries.length;

    const selectedCount =
        Object.keys(selectedObjects).length;


    return (
        <div className="multi-selector">

            <div className="multi-selector-header">
                <div>
                    <div className="multi-selector-title">
                        Chọn đối tượng cho Multi Flow
                    </div>

                    <div className="multi-selector-subtitle">
                        Ngáo đã tìm thấy nhiều nhóm đối tượng cần xác nhận. Anh/chị chọn đủ từng nhóm trước khi thực hiện.
                    </div>
                </div>

                <div className="multi-selector-progress">
                    {selectedCount}/{requiredCount}
                </div>
            </div>


            <div className="multi-selector-body">

                {
                    objectEntries.map(([
                        objectType,
                        candidates
                    ]) => {
                        const selectedObject =
                            selectedObjects?.[objectType];

                        return (
                            <div
                                key={objectType}
                                className="multi-selector-section"
                            >
                                <div className="multi-selector-section-header">

                                    <div className="multi-selector-object-type">
                                        {objectType}
                                    </div>

                                    {
                                        selectedObject && (
                                            <div className="multi-selector-selected-badge">
                                                Đã chọn
                                            </div>
                                        )
                                    }

                                </div>


                                {
                                    !Array.isArray(candidates) ||
                                    candidates.length === 0
                                        ? (
                                            <div className="multi-selector-empty">
                                                Không có ứng viên phù hợp
                                            </div>
                                        )
                                        : (
                                            <div className="multi-selector-list">
                                                {
                                                    candidates.map((
                                                        candidate,
                                                        index
                                                    ) => {
                                                        const selected =
                                                            isSameCandidate(
                                                                selectedObject,
                                                                candidate
                                                            );

                                                        return (
                                                            <button
                                                                key={
                                                                    getCandidateKey(
                                                                        candidate,
                                                                        index
                                                                    )
                                                                }
                                                                type="button"
                                                                className={
                                                                    selected
                                                                        ? "multi-selector-item selected"
                                                                        : "multi-selector-item"
                                                                }
                                                                onClick={() =>
                                                                    handleSelect(
                                                                        objectType,
                                                                        candidate
                                                                    )
                                                                }
                                                            >
                                                                <div className="multi-selector-item-main">
                                                                    <div className="multi-selector-policy-container">

                                                                        <span
                                                                            className={
                                                                                `multi-selector-policy ${candidate.approval_policy}`
                                                                            }
                                                                        >
                                                                            {
                                                                                candidate.approval_policy === "admin_secret"
                                                                                    ? "🔒"
                                                                                    : "🟢"
                                                                            }
                                                                        </span>

                                                                    </div>
                                                                    <span className="multi-selector-check">
                                                                        {
                                                                            selected
                                                                                ? "✓"
                                                                                : ""
                                                                        }
                                                                    </span>

                                                                    <span className="multi-selector-name">
                                                                        {
                                                                            getDisplayValue(
                                                                                candidate
                                                                            )
                                                                        }
                                                                    </span>
                                                                </div>

                                                                {
                                                                    getSecondaryValue(
                                                                        candidate
                                                                    ) && (
                                                                        <div className="multi-selector-secondary">
                                                                            {
                                                                                getSecondaryValue(
                                                                                    candidate
                                                                                )
                                                                            }
                                                                        </div>
                                                                    )
                                                                }
                                                            </button>
                                                        );
                                                    })
                                                }
                                            </div>
                                        )
                                }

                            </div>
                        );
                    })
                }

            </div>

        </div>
    );
}


export default MultiSelector;