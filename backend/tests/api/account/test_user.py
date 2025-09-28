import pytest
from fastapi import status


class TestUser:
    @pytest.mark.asyncio
    async def test_create_user(
            self,
            async_client,
            create_tables,
            get_user_payload,
            async_session,
    ):
        response = await async_client.post(
            "/api/v1/account/users/",
            json=get_user_payload
        )
        assert response.status_code == status.HTTP_201_CREATED


    @pytest.mark.asyncio
    async def test_list_users(
            self,
            async_client,
            create_tables,
            create_test_user,
            async_session
    ):
        response = await async_client.get(
            "/api/v1/account/users/",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == create_test_user.email

    @pytest.mark.asyncio
    async def test_update_user(
            self,
            async_client,
            create_tables,
            get_update_payload,
            create_test_user,
            async_session
    ):
        response = await async_client.put(
            f"/api/v1/account/users/{create_test_user.id}",
            json = get_update_payload
        )

        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["first_name"] == create_test_user.first_name
        assert data["last_name"] == create_test_user.last_name

    @pytest.mark.asyncio
    async def test_delete_user(
            self,
            async_client,
            create_tables,
            create_test_user,
            async_session
    ):
        response = await async_client.delete(
            f"/api/v1/account/users/{create_test_user.id}",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT