
.eml folder
  ↓
read từng email
  ↓
extract subject/from/date/body
  ↓
parse HR form deterministic
  ↓
build employee_extract
  ↓
gọi lại search_tool hiện có
  ↓
build pending_request
  ↓
append vào pending_request.json

React
  cd Onboard_UI_React
  npm run dev

Swagger (FASTAPI)  
uvicorn app.main:app --reload



Thêm Khối hoặc đổi tên Khối :
  Update lại code trong final_resolver.py
  Update file excel sử dụng cho tool
    
Sửa DisplayName phần hiển thị, vd (K.CNTT-HO):
  Update file division_code_map.json



Case Onboard : JWT lưu trên UI và UI gọi trực tiếp API, lấy JWT từ UI
Case AD_Tools : JWT lưu tại peding_action và system call API


REACT UI : Portal layout , dùng react-router-dom

npm install react-router-dom

=============================================
CONTRACT TỪ RESOLVER
============================================
{
  "status": "...",
  "state": "...",
  "next_step": "...",

  "action": "...",

  "target_object_type": "...",

  "resolved_objects": {},

  "candidate_objects": {},

  "proposed_action_payload": {},

  "approval_policy": "..."
}


===============================================
ObjectSelector
===============================================
Render condition :
msg.type === "WAITING_OBJECT_SELECTION"
INPUT:
<Data>
candidate_objects.USER[]
action_id
=========================================
CONFIRM CARD
==========================================
Render condition:
msg.type === "CONFIRM_READY"

ConfirmCard consume: (input)
{
  "action": "...",
  "approval_policy": "...",
  "proposed_action_payload": {
      ...
  }
}

ConfirmCard execute:
executeAction(
    action,
    proposed_action_payload
)
=> payload = data.proposed_action_payload

==========================================
CHAT LOCK
==========================================
Khóa chat :
WAITING_OBJECT_SELECTION
CONFIRM_READY

==========================================
MULTI FRAMEWORK - CASE N-N
==========================================
Luồng hoàn chỉnh :
      User
      ↓
      resolve_action()
      ↓
      candidate_objects
      ↓
      isMultiFlow
      ↓
      MultiSelector
      ↓
      selected_objects
      ↓
      resolved_objects
      ↓
      getMultiApprovalPolicy()
      ↓
      buildActionPayload()
      ↓
      confirmData
      ↓
      MultiConfirmCard
      ↓
      verifySecret()
      ↓
      executeAction()



Multi Flow xuất hiện khi :
    resolved_objects = {}
và  candidate_objects có nhiều hơn 1 giá trị object_type (>=2)

Candidate Object Schema :
  bổ sung "approval_policy" 

MultiSelector :
 Data nhận : msg.data.candidate_objects
      {
    USER: [...],
    GROUP: [...]
      }

 Render theo : 
    Object.entries(
      candidate_objects
    )
Selected Objects :
  schema
    selected_objects: currentSelectedObjects,
    const currentSelectedObjects = {
            ...(resolverData.selected_objects || {}),
            [objectType]: selectedObject

Điều kiện đủ object :
    Object.keys(
        selected_objects
    ).length

    ===

    Object.keys(
        candidate_objects
    ).length
==> selected_object = số lượng object_type trong candidates

Resolved Objects : khi đủ selected_object
      resolvedObjects = {
        ...selectedObjects
    };
  schema : 
        {
          USER: {...},
          GROUP: {...}
      }

Payload : sau khi đủ object từ hàm handleMultiSelect() gọi :
        buildActionPayload(
          action,
          resolvedObjects
      )
  để build payload chuẩn cho từng case : vd User-Group hoặc User-OU

ConfirmData : object trung gian quan trọng nhất. Build trong handleMultiSelect()
  schema : 
      const confirmData = {

      ...resolverData,

      completed: true,

      resolved_objects:
          resolvedObjects,

      selected_objects:
          selectedObjects,

      proposed_action_payload:
          proposedActionPayload,

      approval_policy:
          approvalPolicy
  };

MultiConfirmCard :
 chỉ đọc : resolved_objects, approval_policy, proposed_action_payload

Verify Secret : tách riêng biệt cho single và multi
  Trong multi gắn secret cho từng đối tượng, không lấy approval_policy theo request như single

==========================================
ADD NEW TOOL OBJECT ( base on case add-group)
==========================================
Layer 1 - Tool Search :
 LLM detect :
        {
    "action": "add_group",
    "entities": {
        "users": ["sonnm"],
        "groups": ["VPN Users"]
        }
    }

Layer 2 - Resolver:
  Resolver biết: 
        Action = add_group

        Required Objects:
        - USER
        - GROUP
  Resolver gọi: search_tool

  TH đầy đủ : resolve được ngay các requeriment_object (1-1)
    {
    "resolved_objects": {
        "USER": {...},
        "GROUP": {...}
        }
    }
  --> sinh luôn payload và đi tới confirm
      {
      "group_name": "VPN Users"
      }

  Trường hợp nhiều candidate : 
      {
        "candidate_objects": {
            "USER": [...],
            "GROUP": [...]
        },

        "target_object_type": "USER",

        "status": "NEED_OBJECT_SELECTION"
      }
  --> hiển thị ObjectSelector hoặc MultiSelector

Layer 3 - Schema chuẩn của Object :

  USER :
      {
        "object_type": "USER",

        "display_name": "...",

        "sam_account_name": "...",

        "distinguished_name": "...",

        "approval_policy": "normal"
      }
  GROUP :
      {
          "object_type": "GROUP",

          "group_name": "...",

          "distinguished_name": "...",

          "approval_policy": "admin_secret"
      }

  OU :
      {
        "object_type": "OU",

        "ou": "...",

        "distinguished_name": "...",

        "approval_policy": "normal"
      }