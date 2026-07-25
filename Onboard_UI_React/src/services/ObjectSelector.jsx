import "./ObjectSelector.css";
function ObjectSelector({
    Data,
    onSelect
}) {
    const completed =
    Data?.completed || false;

    const selectedUser =
    Data?.selectedUser;
    console.log(
        "COMPLETED =",
        completed
    );

    console.log(
        "SELECTED USER =",
        selectedUser
    );
    const users =
        Data?.candidate_objects?.USER || [];

        return (
            <div className="object-selector">

                {users.map((user) => {

                    const isSelected =
                        Data?.selectedUser?.sam_account_name
                        ===
                        user.sam_account_name;

                    return (

                        <button
                            disabled={completed}
                            key={user.distinguished_name}
                            className={
                                isSelected
                                    ? "object-option selected"
                                    : "object-option"
                            }
                            onClick={() =>
                                onSelect(
                                    Data,
                                    user
                                )
                            }
                        >
                            <div className="object-option-title">

                                {isSelected && completed && "✅ Đã chọn: "}

                                {user.display_name}

                            </div>
                            <div className="object-sam">
                                ({user.sam_account_name})
                            </div>
                        </button>

                    );

                })}

            </div>
        );
}

export default ObjectSelector;