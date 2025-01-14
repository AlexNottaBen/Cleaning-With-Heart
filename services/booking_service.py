from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from database.connector import get_session
from enums.building_type import BuildingType
from enums.selected_service import SelectedService
from exceptions.entity_not_found_exception import EntityNotFoundException
from models.booking import Booking


class BookingService:

    def create_booking(
        self,
        first_name: str,
        last_name: str,
        phone_number: str,
        email: str,
        street: str,
        start_datetime: datetime,
        finish_datetime: datetime,
        selected_service: SelectedService,
        clean_oven: bool,
        clean_windows: bool,
        clean_basement: bool,
        move_in_cleaning: bool,
        move_out_cleaning: bool,
        clean_fridge: bool,
        building: BuildingType,
        rooms_number: int,
        square_feet: int,
        use_equipment: bool,
        session: Session = get_session(),
    ) -> None:
        booking = Booking(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            street=street,
            start_datetime=start_datetime,
            finish_datetime=finish_datetime,
            selected_service=selected_service,
            clean_oven=clean_oven,
            clean_windows=clean_windows,
            clean_basement=clean_basement,
            move_in_cleaning=move_in_cleaning,
            move_out_cleaning=move_out_cleaning,
            clean_fridge=clean_fridge,
            building=building,
            rooms_number=rooms_number,
            square_feet=square_feet,
            use_equipment=use_equipment,
        )
        session.add(booking)
        session.commit()
        session.close()

    def retrieve_bookings(
        self,
        session: Session = get_session(),
    ) -> Optional[List[Booking]]:
        return session.query(Booking).all()

    def retrieve_booking_by_id(
        self,
        booking_id: int,
        session: Session = get_session(),
    ) -> Optional[Booking]:
        return session.query(Booking).filter(Booking.id == booking_id).first()

    def update_booking(
        self,
        booking_id: int,
        first_name: str,
        last_name: str,
        phone_number: str,
        email: str,
        street: str,
        start_datetime: datetime,
        finish_datetime: datetime,
        selected_service: SelectedService,
        clean_oven: bool,
        clean_windows: bool,
        clean_basement: bool,
        move_in_cleaning: bool,
        move_out_cleaning: bool,
        clean_fridge: bool,
        building: BuildingType,
        rooms_number: int,
        square_feet: int,
        use_equipment: bool,
        session: Session = get_session(),
    ) -> None:
        booking: Optional[Booking] = self.retrieve_booking_by_id(
            booking_id=booking_id, session=session
        )
        if booking:
            booking.first_name = first_name
            booking.last_name = last_name
            booking.phone_number = phone_number
            booking.email = email
            booking.street = street
            booking.start_datetime = start_datetime
            booking.finish_datetime = finish_datetime
            booking.selected_service = selected_service
            booking.clean_oven = clean_oven
            booking.clean_windows = clean_windows
            booking.clean_basement = clean_basement
            booking.move_in_cleaning = move_in_cleaning
            booking.move_out_cleaning = move_out_cleaning
            booking.clean_fridge = clean_fridge
            booking.building = building
            booking.rooms_number = rooms_number
            booking.square_feet = square_feet
            booking.use_equipment = use_equipment
            session.commit()
            session.close()
        else:
            raise EntityNotFoundException("Booking not found!")

    def delete_booking(
        self,
        booking_id: int,
        session: Session = get_session(),
    ) -> None:
        booking: Optional[Booking] = self.retrieve_booking_by_id(
            booking_id=booking_id, session=session
        )
        if booking:
            session.delete(booking)
            session.commit()
            session.close()
        else:
            raise EntityNotFoundException("Booking not found!")
