from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from app.auto_engine.models.employee_offboarding import (
    EmployeeOffboardingApiRequest
)
from app.api.workflow_request import create_offboarding_plan
from app.auth.dependencies import (
    require_service_token,
    require_integration_token
)
from app.auth.integration_registry import INTEGRATION_CLIENTS
from app.auth.jwt_handler import create_integration_token
from app.auth.integration_token_request import IntegrationTokenRequest
router = APIRouter()


@router.post(
    "/employee-offboarding"
)
def service_employee_offboarding(
    source_request:
        EmployeeOffboardingApiRequest,

    claims=Depends(
        require_service_token
    )
):

    try:

        return create_offboarding_plan(
            source_request
        )

    except ValueError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )

@router.post(
    "/integration/token"
)
def integration_token(
    request:
        IntegrationTokenRequest
):

    client = (
        INTEGRATION_CLIENTS.get(
            request.client_id
        )
    )

    if not client:

        raise HTTPException(
            status_code=401,
            detail="Invalid client_id"
        )

    if (
        not client["enabled"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Client disabled"
        )

    if (
        client["client_secret"]
        != request.client_secret
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid client_secret"
        )

    token = (
        create_integration_token(
            request.client_id
        )
    )

    return {

        "access_token":
            token,

        "token_type":
            "bearer",

        "client_id":
            request.client_id,
    }

@router.post(
    "/integration/employee-offboarding"
)
def integration_employee_offboarding(

    source_request:
        EmployeeOffboardingApiRequest,

    claims=Depends(
        require_integration_token
    )
):

    try:

        return create_offboarding_plan(
            source_request
        )

    except ValueError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )
    