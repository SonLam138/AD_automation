import "./ObjectSelector.css";
function GroupSelector({
    Data,
    onSelect
}) {
    const completed =
    Data?.completed || false;

    const selectedGroup =
    Data?.selectedGroup;

    const groups =
    Data?.candidate_objects?.GROUP || [];
        return (
            <div className="object-selector">

                {groups.map((group) => {

                    const isSelected =
                        Data?.selectedGroup?.cn
                        ===
                        group.cn;

                    return (

                        <button
                            disabled={completed}
                            key={group.cn}
                            className={
                                isSelected
                                    ? "object-option selected"
                                    : "object-option"
                            }
                            onClick={() =>
                                onSelect(
                                    Data,
                                    group
                                )
                            }
                        >
                            <div className="object-option-title">

                                {isSelected && completed && "✅ Đã chọn: "}

                                {group.name}

                            </div>
                            <div className="object-sam">
                                ({group.cn})
                            </div>
                        </button>

                    );

                })}

            </div>
        );
}

export default GroupSelector;