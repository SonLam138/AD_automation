import "./ObjectSelector.css";

function ObjectSelector({
    Data,
    onSelect
}) {

    const completed =
        Data?.completed || false;

    const objectType =
        Data?.target_object_type;

    const objects =
        Data?.candidate_objects?.[
            objectType
        ] || [];

    const selectedObject =
        Data?.selectedObject;

    const getTitle = (
        item
    ) => {

        return (
            item.display_name ||
            item.computer_name ||
            item.ou ||
            item.name ||
            item.cn ||
            "Unknown"
        );
    };

    const getSubtitle = (
        item
    ) => {

        return (
            item.sam_account_name ||
            item.dns_host_name ||
            item.distinguished_name ||
            ""
        );
    };

    const isSameObject = (
        selected,
        candidate
    ) => {

        if (
            !selected ||
            !candidate
        ) {
            return false;
        }

        return (
            selected.distinguished_name
            ===
            candidate.distinguished_name
        );
    };

    return (

        <div className="object-selector">

            {objects.map((item) => {

                const isSelected =
                    isSameObject(
                        selectedObject,
                        item
                    );

                return (

                    <button
                        disabled={completed}
                        key={
                            item.distinguished_name
                        }
                        className={
                            isSelected
                                ? "object-option selected"
                                : "object-option"
                        }
                        onClick={() =>
                            onSelect(
                                Data,
                                item
                            )
                        }
                    >

                        <div className="object-option-title">

                            {item.approval_policy === "admin_secret" &&
                                "🔐 "}

                            {isSelected &&
                                completed &&
                                "✅ Đã chọn: "}

                            {getTitle(item)}

                        </div>

                        {!!getSubtitle(item) && (

                            <div className="object-sam">
                                (
                                {getSubtitle(
                                    item
                                )}
                                )
                            </div>

                        )}

                    </button>

                );

            })}

        </div>

    );

}

export default ObjectSelector;