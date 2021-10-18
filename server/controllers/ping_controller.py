from fastapi import APIRouter, Response
from fastapi import status


router = APIRouter()
ping_router = dict(
    router=router,
    prefix="/ping",
    tags=["Ping"],
)


@router.get(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Endpoint para testar o microsserviço'
)
async def ping():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

