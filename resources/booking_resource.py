from datetime import datetime, timedelta
from typing import Optional, Union

from flask import Response, json, request
from flask_login import login_required
from flask_restful import Resource
from pydantic import EmailStr, ValidationError

from common.exceptions.entity_not_found_exception import EntityNotFoundError
from common.utils.datetime_util import iso_string_to_datetime_utc
from enums.building_type import BuildingType
from enums.selected_service import SelectedService
from models.booking import Booking
from models.customer import Customer
from schemes.booking_scheme import BookingScheme
from schemes.customer_scheme import CustomerScheme
from services.booking_service import BookingService
from services.customer_service import CustomerService


class BookingResource(Resource):

    def __init__(self):
        self.booking_service = BookingService()
        self.customer_service = CustomerService()

    @login_required
    def get(self, booking_id: int):
        try:
            booking: Booking = self.booking_service.retrieve_booking_by_id(
                booking_id=booking_id
            )
            return Response(
                status=200,
                content_type="application/json",
                response=json.dumps(booking.to_dict()),
            )
        except EntityNotFoundError as e:
            return Response(
                status=404,
                content_type="application/json",
                response=json.dumps({"message": str(e)}),
            )

    @login_required
    def put(self, booking_id: int) -> Response:

        try:
            data: dict = request.json
            customer_id: Optional[int] = (
                int(
                    data["customerId"],
                )
                if data.get("customerId")
                else None
            )
            first_name: str = data.get("firstName")
            last_name: str = data.get("lastName", "")
            phone_number: str = data.get("phoneNumber")
            email: Union[EmailStr, str] = data.get("email")
            street: str = data.get("street")

            start_datetime: datetime = iso_string_to_datetime_utc(
                data.get("startDatetime"),
            )
            cleaning_master_name: str = data.get("cleaningMasterName") or None
            default_cleaning_duration = timedelta(hours=2)
            finish_datetime: datetime = (
                iso_string_to_datetime_utc(data.get("finishDatetime"))
                if data.get("finishDatetime")
                else start_datetime + default_cleaning_duration
            )
            selected_service: Union[SelectedService, str] = data.get(
                "selectedService",
            )

            # Checkboxes
            has_clean_oven = bool(data.get("hasCleanOven"))
            has_clean_windows = bool(data.get("hasCleanWindows"))
            has_clean_basement = bool(data.get("hasCleanBasement"))
            has_move_in_cleaning = bool(data.get("hasMoveInCleaning"))
            has_move_out_cleaning = bool(data.get("hasMoveOutCleaning"))
            has_clean_fridge = bool(data.get("hasCleanFridge"))
            building: Union[BuildingType, str] = data.get("building")
            rooms_number = abs(int(data.get("roomsNumber")))
            square_feet = abs(int(data.get("squareFeet")))
            has_own_equipment = bool(data.get("hasOwnEquipment"))

            customer_scheme: Optional[CustomerScheme] = None

            if not customer_id:
                customer_scheme = CustomerScheme(
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    email=email,
                    street=street,
                )

            booking_scheme = BookingScheme(
                start_datetime=start_datetime,
                finish_datetime=finish_datetime,
                selected_service=selected_service,
                has_clean_oven=has_clean_oven,
                has_clean_windows=has_clean_windows,
                has_clean_basement=has_clean_basement,
                has_move_in_cleaning=has_move_in_cleaning,
                has_move_out_cleaning=has_move_out_cleaning,
                has_clean_fridge=has_clean_fridge,
                cleaning_master_name=cleaning_master_name,
                building=building,
                rooms_number=rooms_number,
                square_feet=square_feet,
                has_own_equipment=has_own_equipment,
            )

        except ValidationError as error:
            return Response(
                status=422,
                content_type="application/json",
                response=error.json(),
            )
        except KeyError as error:
            return Response(
                status=400,
                content_type="application/json",
                response=json.dumps({"message": "Invalid key: " + str(error)}),
            )
        except (ValueError, TypeError) as error:
            return Response(
                status=400,
                content_type="application/json",
                response=json.dumps({"message": str(error)}),
            )

        try:
            if not customer_id:
                customer: Customer = self.customer_service.create_customer(
                    first_name=customer_scheme.first_name,
                    last_name=customer_scheme.last_name,
                    phone_number=customer_scheme.phone_number,
                    email=customer_scheme.email,
                    street=customer_scheme.street,
                )
                customer_id = customer.id

            self.booking_service.update_booking(
                booking_id=booking_id,
                customer_id=customer_id,
                start_datetime=booking_scheme.start_datetime,
                finish_datetime=booking_scheme.finish_datetime,
                selected_service=booking_scheme.selected_service,
                has_clean_oven=booking_scheme.has_clean_oven,
                has_clean_windows=booking_scheme.has_clean_windows,
                has_clean_basement=booking_scheme.has_clean_basement,
                has_move_in_cleaning=booking_scheme.has_move_in_cleaning,
                has_move_out_cleaning=booking_scheme.has_move_out_cleaning,
                has_clean_fridge=booking_scheme.has_clean_fridge,
                building=booking_scheme.building,
                rooms_number=booking_scheme.rooms_number,
                square_feet=booking_scheme.square_feet,
                has_own_equipment=booking_scheme.has_own_equipment,
                cleaning_master_name=booking_scheme.cleaning_master_name,
            )
            return Response(
                status=200,
                content_type="application/json",
                response=json.dumps({"message": "Booking updated successfully!"}),
            )
        except EntityNotFoundError as e:
            return Response(
                status=404,
                content_type="application/json",
                response=json.dumps({"message": str(e)}),
            )

    @login_required
    def patch(self, booking_id: int):
        data = request.json
        try:
            start_datetime: datetime = iso_string_to_datetime_utc(data.get("start"))
            finish_datetime: datetime = iso_string_to_datetime_utc(data.get("end"))
        except (ValueError, TypeError) as error:
            return Response(
                status=400,
                content_type="application/json",
                response=json.dumps({"message": str(error)}),
            )

        try:
            self.booking_service.update_booking_range(
                booking_id=booking_id,
                start_datetime=start_datetime,
                finish_datetime=finish_datetime,
            )
            return Response(
                status=200,
                content_type="application/json",
                response=json.dumps({"message": "Booking updated successfully!"}),
            )
        except EntityNotFoundError as e:
            return Response(
                status=404,
                content_type="application/json",
                response=json.dumps({"message": str(e)}),
            )

    @login_required
    def delete(self, booking_id: int) -> Response:
        try:
            self.booking_service.delete_booking(booking_id=booking_id)
            return Response(
                status=200,
                content_type="application/json",
                response=json.dumps({"message": "Booking deleted successfully!"}),
            )
        except EntityNotFoundError as e:
            return Response(
                status=404,
                content_type="application/json",
                response=json.dumps({"message": str(e)}),
            )
