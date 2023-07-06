from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import exceptions, status, utils
from rest_framework import status


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    (
                        "next",
                        self.page.next_page_number() if self.page.has_next() else None,
                    ),
                    (
                        "previous",
                        self.page.previous_page_number()
                        if self.page.has_previous()
                        else None,
                    ),
                    ("page", self.page.number),
                    ("results", data),
                ]
            )
        )


class CustomJSONRenderer(JSONRenderer):
    """Override the default JSON renderer to be consistent and have additional keys"""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context["response"].status_code
        if status_code == 500:
            status_code = 400
            renderer_context["response"].status_code = status_code
        status = True if status_code < 400 else False
        message = "successful" if status else "failed"
        # when response data is a list, convert to dict
        if data is None:
            data = {"status": status, "message": message, "data": data}
        elif type(list(data.values())[0]) == str:
            data = {"status": status, "message": message, "data": data}
        elif type(data) == utils.serializer_helpers.ReturnDict:
            try:
                if type(list(data.values())[0][0]) == exceptions.ErrorDetail:
                    error = list(data.values())[0][0]
                    code = list(data.values())[0][0].code
                    key = list(data.keys())[0]
                    message = (
                        f"{key}: {error}"
                        if key != "non_field_errors" and code not in ("unique",)
                        else error
                    )
                    data = {"status": status, "message": message, "data": {}}
                elif (type(list(list(data.values())[0][0].values())[0][0])
                    == exceptions.ErrorDetail
                ):
                    error = list(list(data.values())[0][0].values())[0][0]

                    key = list(list(data.values())[0][0].keys())[0]
                    message = f"{key}: {error}" if key != "non_field_errors" else error
                    data = {"status": status, "message": message, "data": {}}
            except KeyError:
                if (
                    type(list(list(data.values())[0].values())[0][0])
                    == exceptions.ErrorDetail
                ):
                    error = list(list(data.values())[0].values())[0][0]
                    key = list(data.keys())[0]

                    message = f"{key}: {error}" if key != "non_field_errors" else error
                    data = {"status": status, "message": message, "data": {}}

            except TypeError:
                data = {"status": status, "message": message, "data": data}
        elif isinstance(data, list):
            if data and type(data[0]) == exceptions.ErrorDetail:
                data = {"status": status, "message": data[0], "data": {}}
            else:
                data = {"status": status, "message": message, "data": data}
        elif data is None:
            data = {"status": status, "message": message, "data": {}}

        # if response data is not well formated dict, and not an error response, convert to right format
        elif (
            isinstance(data, OrderedDict)
            and ("data" not in data)
            and ("non_field_errors" not in data)
        ):
            data = {
                "status": status,
                "message": message,
                "data": data,
            }
        elif isinstance(data, dict) and (
            "detail" in data or "non_field_errors" in data
        ):
            res = list(data.values())[0]
            data = {
                "status": status,
                "message": res[0] if isinstance(res, list) else res,
                "data": {},
            }

        # if not `status` in response, add status
        if "status" not in data:
            data["status"] = status

        # if no `message` in response, add message based on status
        if "message" not in data:
            data["message"] = message

        # Added this so we can use `.move_to_end` to make `status` & `message` come on top
        # if isinstance(data, dict):
        # data = OrderedDict(data.items())

        # removing to increase spead, since this is O(N), and only needed when
        # returning some error responses
        # data.move_to_end('message', last=False)
        # data.move_to_end('status', last=False)

        return super().render(data, accepted_media_type, renderer_context)



class SuccessResponse:
    """Standardise API Responses and add additional keys"""

    def __new__(
        cls, data=None, message="successful", status=status.HTTP_200_OK, list_mode=False
    ):
        return Response(
            {
                "status": True,
                "message": message,
                "data": data if data else [] if list_mode else {},
            },
            status,
        )


class FailureResponse:
    def __new__(cls, message="error", status=status.HTTP_400_BAD_REQUEST):
        return Response({"status": False, "message": message}, status)
