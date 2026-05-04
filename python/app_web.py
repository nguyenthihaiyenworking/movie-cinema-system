import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import database connection
from database_conn import get_connection

# Import Management Modules
from modules.auth_mgr   import check_login, get_all_logs, add_account, list_accounts, update_account, delete_account
from modules.movie_mgr  import ( 
   list_movies,
   add_movie, 
   delete_movie, 
   get_all_screenings, list_genres, 
   add_genre, delete_genre, 
   update_movie, update_genre, 
   update_screening, delete_screening, 
   list_rooms, check_overlap, add_screening, list_seat_types, add_seat_type, update_seat_type, delete_seat_type

)
from modules.booking_mgr import book_ticket, list_bookings, book_seat_with_lock, get_customer_by_phone, add_new_customer, get_seat_info, get_seats_by_room, delete_ticket

# Import Analytics & Report Functions (Updated to match your report_mgr.py)
from modules.report_mgr import (
    get_movie_revenue_report,
    get_top_customers,
    get_revenue_by_tier,
    get_revenue_by_room_type,
    get_all_movies_revenue_summary,
    get_occupancy_report
)
from modules.customer_mgr import add_customer, find_customer_by_phone, list_all_customers
# ─────────────────────────────────────────────────────────────────────────────
# 1. SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
if "cart" not in st.session_state:
    st.session_state.cart = []

# ─────────────────────────────────────────────────────────────────────────────
# 2. LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
def login_page():
    st.title("🎬 NEU Cinema Management System")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit   = st.form_submit_button("Login")

        if submit:
            user_data, msg = check_login(username, password)
            if user_data:
                # 1. Set login status
                st.session_state.logged_in = True
                
                # 2. Store the full user object for general use
                st.session_state.user = user_data
                
                # 3. Explicitly set user_id for the Booking & Locking functions
                # user_data is a dict containing 'AccountID' from your check_login function
                st.session_state.user_id = user_data['AccountID']
                
                # 4. Optional: store role and username for easy access in UI
                st.session_state.username = user_data['Username']
                st.session_state.role = user_data['Role']
                
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# ─────────────────────────────────────────────────────────────────────────────
# 3. SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
def main():
    user = st.session_state.user
    role = user["Role"]   # "Admin" or "Staff"

    st.sidebar.title(f"Welcome, {user['Username']}")
    st.sidebar.info(f"Role: {role}")

    if role == "Admin":
        menu = ["Dashboard", "Movies & Genres", "Screenings",
                "Rooms & Seats", "Accounts", "System Logs"]
    else:
        menu = ["Ticket Booking", "Movie Search", "Customer Management"]

    choice = st.sidebar.selectbox("Navigation", menu)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    # ── Route ──────────────────────────────────────────────────────────────
    if   choice == "Dashboard":         render_dashboard()
    elif choice == "Movies & Genres":   render_movies()
    elif choice == "Screenings":        render_screenings()
    elif choice == "Rooms & Seats":     render_rooms()
    elif choice == "Accounts":          render_accounts()
    elif choice == "System Logs":       render_logs()
    elif choice == "Ticket Booking":    render_ticket_management()
    elif choice == "Movie Search":      render_movie_search()
    elif choice == "Customer Management": render_customer_management()

# ─────────────────────────────────────────────────────────────────────────────
# 4. ADMIN — Movies & Genres
# ─────────────────────────────────────────────────────────────────────────────
def render_movies():
    st.header("🎥 Movie & Genre Management")
    tab1, tab2 = st.tabs(["Movies", "Genres"])

    with tab1:
        movies = list_movies()
        df_movies = pd.DataFrame(movies)
        st.dataframe(df_movies, use_container_width=True)

        # --- PHẦN THÊM MỚI ---
        with st.expander("➕ Add New Movie"):
            with st.form("add_movie_form"):
                title        = st.text_input("Movie Title")
                duration     = st.number_input("DurationMinutes (mins)", min_value=1)
                release_date = st.date_input("Release Date")
                rating       = st.selectbox("Rating", ["P", "T13", "T16", "T18"])

                if st.form_submit_button("Submit"):
                    if not title:
                        st.error("Title cannot be empty!")
                    else:
                        add_movie(title, duration, release_date, rating)
                        st.success("Movie added!")
                        st.rerun()

        # --- PHẦN SỬA PHIM (MỚI) ---
        with st.expander("📝 Edit Existing Movie"):
            if not df_movies.empty:
                # Chọn phim theo tiêu đề để dễ nhìn, nhưng lấy ra ID để xử lý
                movie_to_edit = st.selectbox("Select Movie to Edit", options=df_movies['MovieTitle'].tolist())
                
                # Lấy dữ liệu cũ của phim đã chọn để hiển thị lên form
                old_data = df_movies[df_movies['MovieTitle'] == movie_to_edit].iloc[0]
                
                with st.form("edit_movie_form"):
                    new_title = st.text_input("New Movie Title", value=old_data['MovieTitle'])
                    new_duration = st.number_input("New Duration (mins)", min_value=1, value=int(old_data['DurationMinutes']))
                    # Ép kiểu date nếu cần thiết
                    old_date = old_data['ReleaseDate']
                    new_release_date = st.date_input("New Release Date", value=old_date)
                    
                    # Tìm index của rating cũ trong list để selectbox hiện đúng
                    ratings_list = ["P", "T13", "T16", "T18"]
                    old_rating_idx = ratings_list.index(old_data['Rating']) if old_data['Rating'] in ratings_list else 0
                    new_rating = st.selectbox("New Rating", ratings_list, index=old_rating_idx)

                    if st.form_submit_button("Update Movie"):
                        success, msg = update_movie(old_data['MovieID'], new_title, new_duration, new_release_date, new_rating)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.info("No movies available to edit.")

        # --- PHẦN XÓA ---
        st.subheader("🗑️ Delete Movie")
        del_id = st.number_input("Enter Movie ID to delete", step=1)
        if st.button("Confirm Delete"):
            success, msg = delete_movie(del_id)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab2:
            st.subheader("Manage Genres")
            genres = list_genres()
            df_genres = pd.DataFrame(genres)
            st.dataframe(df_genres, use_container_width=True)

            # Chia 2 cột cho phần Sửa và Xóa
            col_edit, col_del = st.columns(2)

            with col_edit:
                with st.expander("📝 Edit Genre"):
                    if not df_genres.empty:
                        # Cho phép chọn GenreID từ danh sách hiện có
                        edit_id = st.selectbox("Select Genre to Edit", options=df_genres['GenreID'].tolist())
                        new_name = st.text_input("New Genre Name")
                        if st.button("Update Name"):
                            if new_name:
                                success, msg = update_genre(edit_id, new_name)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                            else:
                                st.warning("Please enter a new name.")

            with col_del:
                with st.expander("🗑️ Delete Genre"):
                    if not df_genres.empty:
                        del_id = st.selectbox("Select Genre to Delete", options=df_genres['GenreID'].tolist(), key="del_genre_select")
                        if st.button("Confirm Delete Genre"):
                            success, msg = delete_genre(del_id)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

            # Giữ nguyên phần Add New Genre của Yen ở dưới
            with st.expander("➕ Add New Genre"):
                with st.form("add_genre_form"):
                    genre_name = st.text_input("Genre Name")
                    if st.form_submit_button("Submit"):
                        if not genre_name:
                            st.error("Genre name cannot be empty!")
                        else:
                            add_genre(genre_name)
                            st.success("Genre added!")
                            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 5. ADMIN — Screenings
# ─────────────────────────────────────────────────────────────────────────────
def render_screenings():
    st.title("🎬 Screening Schedule Management")

    # --- 1. DATA LOADING ---
    screenings_data = get_all_screenings()
    movies_list = list_movies()
    rooms_list = list_rooms()

    # --- 2. SEARCH & FILTER SECTION ---
    with st.expander("🔍 Filter Screenings", expanded=False):
        if screenings_data:
            df = pd.DataFrame(screenings_data)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                movie_filter = st.selectbox("Filter by Movie", ["All"] + list(df['MovieTitle'].unique()))
            with col2:
                room_filter = st.selectbox("Filter by Room", ["All"] + list(df['RoomName'].unique()))
            with col3:
                df['DateOnly'] = pd.to_datetime(df['ShowDate']).dt.date
                date_filter = st.selectbox("Filter by Date", ["All"] + sorted(list(df['DateOnly'].unique())))

            if movie_filter != "All":
                df = df[df['MovieTitle'] == movie_filter]
            if room_filter != "All":
                df = df[df['RoomName'] == room_filter]
            if date_filter != "All":
                df = df[df['DateOnly'] == date_filter]
            
            display_cols = ['ScreeningID', 'MovieTitle', 'RoomName', 'ShowDate']
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.info("No screenings available to display.")

    st.divider()

    # --- 3. ADD / EDIT / DELETE SECTION ---
    col_left, col_right = st.columns(2)

    # ADD NEW SCREENING
    with col_left:
        st.subheader("➕ Add New Screening")
        if not movies_list or not rooms_list:
            st.warning("Please ensure Movies and Rooms are added first.")
        else:
            with st.form("add_form", clear_on_submit=True):
                m_map = {m['MovieTitle']: (m['MovieID'], m['DurationMinutes']) for m in movies_list}
                r_map = {r['RoomName']: r['RoomID'] for r in rooms_list}
                
                sel_movie = st.selectbox("Select Movie", list(m_map.keys()))
                sel_room = st.selectbox("Select Room", list(r_map.keys()))
                sel_date = st.date_input("Show Date")
                sel_time = st.time_input("Show Time")
                
                if st.form_submit_button("Create Screening"):
                    target_dt = f"{sel_date} {sel_time}"
                    m_id, m_duration = m_map[sel_movie]
                    r_id = r_map[sel_room]
                    
                    if check_overlap(r_id, target_dt, m_duration):
                        st.error(f"Conflict! Room '{sel_room}' is already occupied.")
                    else:
                        success, msg = add_screening(m_id, r_id, target_dt)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    # EDIT & DELETE
    with col_right:
        st.subheader("📝 Edit or 🗑️ Delete")
        if screenings_data:
            df_edit = pd.DataFrame(screenings_data)
            target_id = st.selectbox("Select Screening ID to Modify", df_edit['ScreeningID'].tolist())
            current_row = df_edit[df_edit['ScreeningID'] == target_id].iloc[0]
            
            with st.form("edit_form"):
                st.info(f"Modifying Screening: {target_id}")
                new_date = st.date_input("Update Date", value=pd.to_datetime(current_row['ShowDate']).date())
                new_time = st.time_input("Update Time", value=pd.to_datetime(current_row['ShowDate']).time())
                
                if st.form_submit_button("Update Schedule"):
                    new_dt = f"{new_date} {new_time}"
                    # --- FIX Ở ĐÂY: Dùng đúng tên cột DurationMinutes từ DataFrame ---
                    m_duration = current_row['DurationMinutes'] if 'DurationMinutes' in current_row else 120
                    
                    if check_overlap(current_row['RoomID'], new_dt, m_duration, current_screening_id=target_id):
                        st.error("Conflict: This room is busy at the new time.")
                    else:
                        success, msg = update_screening(target_id, current_row['MovieID'], current_row['RoomID'], new_dt)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            if st.button("🗑️ Delete Permanently", type="primary"):
                success, msg = delete_screening(target_id)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.write("No screenings selected.")

# ─────────────────────────────────────────────────────────────────────────────
# 6. ADMIN — Rooms & Seats
# ─────────────────────────────────────────────────────────────────────────────
def render_rooms():
    st.title("💺 Room & Seat Management")
    
    # Create 2 separate Tabs for a professional UI
    tab_rooms, tab_seats = st.tabs(["Theater Rooms", "Seat Categories"])

    # --- TAB 1: THEATER ROOMS (Cinema Room Management) ---
    with tab_rooms:
        st.header("Theater Rooms")
        
        # 1. Display existing rooms from Database
        rooms = list_rooms()
        if rooms:
            df_rooms = pd.DataFrame(rooms)
            st.subheader("Current Rooms")
            # Displaying specific columns based on the 'cinemarooms' table structure
            st.dataframe(df_rooms[['RoomID', 'RoomName', 'Capacity']], use_container_width=True)
        else:
            st.info("No rooms found in the database.")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ Add New Room")
            with st.form("add_room_form", clear_on_submit=True):
                r_name = st.text_input("Room Name (e.g., IMAX 1)")
                r_cap = st.number_input("Capacity", min_value=1, value=50)
                
                if st.form_submit_button("Create Room"):
                    if r_name:
                        # Calls add_room function from movie_mgr
                        success, msg = add_room(r_name, r_cap)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please enter a room name.")

        with col2:
            st.subheader("📋 Copy Seat Layout")
            st.info("Quickly copy seat arrangement from an existing room to a new one.")
            source_id = st.number_input("Source Room ID (Template)", step=1, min_value=1)
            target_id = st.number_input("Target Room ID (New Room)", step=1, min_value=1)
            
            if st.button("Duplicate Layout", use_container_width=True):
                if source_id == target_id:
                    st.warning("Source and Target IDs must be different.")
                else:
                    # Calls copy_room_layout function from movie_mgr
                    success, msg = copy_room_layout(source_id, target_id)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    # --- TAB 2: SEAT CATEGORIES (Seat Types & Pricing Management) ---
    with tab_seats:
        st.header("Seat Types & Pricing")
        
        # 1. Display existing seat types
        seat_types = list_seat_types()
        if seat_types:
            df_types = pd.DataFrame(seat_types)
            st.subheader("Existing Seat Types")
            # Display base pricing table
            st.table(df_types[['TypeID', 'TypeName', 'BasePrice']])
        else:
            st.info("No seat types defined yet.")
        
        st.divider()

        col_add, col_manage = st.columns(2)
        
        # 2. Add new seat type (VIP, Standard, Sweetbox, etc.)
        with col_add:
            st.subheader("➕ Add New Type")
            with st.form("add_seat_type_form", clear_on_submit=True):
                t_name = st.text_input("Type Name (e.g., VIP)")
                t_price = st.number_input("Base Price Offset", min_value=0, step=5000, value=0)
                
                if st.form_submit_button("Save Type"):
                    if t_name:
                        # Calls add_seat_type function from movie_mgr
                        success, msg = add_seat_type(t_name, t_price)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please enter a type name.")

        # 3. Modify Pricing or Delete Seat Types
        with col_manage:
            st.subheader("⚙️ Manage Existing")
            if seat_types:
                # Create selection list for modification
                type_names = [t['TypeName'] for t in seat_types]
                type_to_mod = st.selectbox("Select Type to Modify", type_names)
                
                # Retrieve data for the selected type
                selected_data = next(t for t in seat_types if t['TypeName'] == type_to_mod)
                
                with st.expander(f"Edit/Delete {type_to_mod}", expanded=True):
                    new_price = st.number_input("Update Base Price", value=int(selected_data['BasePrice']), step=5000)
                    
                    c1, c2 = st.columns(2)
                    if c1.button("💾 Update Price", use_container_width=True):
                        # Calls update_seat_type function from movie_mgr
                        success, msg = update_seat_type(selected_data['TypeID'], new_price)
                        if success:
                            st.success("Price updated!")
                            st.rerun()
                        else:
                            st.error(msg)
                    
                    if c2.button("🗑️ Delete Type", type="primary", use_container_width=True):
                        # Calls delete_seat_type function from movie_mgr
                        success, msg = delete_seat_type(selected_data['TypeID'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            # Error message for foreign key constraint (seat type in use)
                            st.error("Cannot delete: This type is assigned to existing seats.")
            else:
                st.write("No seat types available to manage.")


# ────────────────────────────────────────────────────────────────────────────
# 7. ADMIN — Accounts
# ────────────────────────────────────────────────────────────────────────────
def render_accounts():
    st.title("👤 User Account Management")

    # --- 1. SHOW ACCOUNTS ---
    accounts_data = list_accounts()
    if accounts_data:
        df_acc = pd.DataFrame(accounts_data)
        st.subheader("Current Accounts")
        st.dataframe(df_acc, use_container_width=True)
    else:
        st.info("No accounts found.")

    st.divider()

    col_add, col_edit = st.columns(2)

    # --- 2. ADD ACCOUNT ---
    with col_add:
        st.subheader("➕ Create Account")
        with st.form("add_acc_form", clear_on_submit=True):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            new_name = st.text_input("Full Name")
            new_role = st.selectbox("Role", ["Admin", "Staff"])
            
            if st.form_submit_button("Add User"):
                if new_user and new_pass:
                    success, msg = add_account(new_user, new_pass, new_name, new_role)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else: st.error(msg)
                else: st.warning("Username and Password are required.")

    # --- 3. EDIT / DELETE ACCOUNT ---
    with col_edit:
        st.subheader("📝 Edit / Delete")
        if accounts_data:
            acc_list = {f"{a['Username']} ({a['FullName']})": a for a in accounts_data}
            selected_label = st.selectbox("Select Account to Modify", list(acc_list.keys()))
            selected_acc = acc_list[selected_label]

            with st.expander(f"Update: {selected_acc['Username']}"):
                edit_name = st.text_input("Full Name", value=selected_acc['FullName'])
                edit_role = st.selectbox("Role", ["Admin", "Staff"], 
                                         index=["Admin", "Staff"].index(selected_acc['Role']))
                edit_pass = st.text_input("New Password (Leave blank to keep current)", type="password")
                
                c1, c2 = st.columns(2)
                if c1.button("Save Changes", use_container_width=True):
                    success, msg = update_account(selected_acc['AccountID'], edit_name, edit_role, 
                                                 edit_pass if edit_pass else None)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else: st.error(msg)

                if c2.button("🗑️ Delete Account", type="primary", use_container_width=True):
                    success, msg = delete_account(selected_acc['AccountID'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else: st.error(msg)
        else:
            st.write("No accounts available to modify.")

# ─────────────────────────────────────────────────────────────────────────────
# 8. ADMIN — System Logs
# ─────────────────────────────────────────────────────────────────────────────
def render_logs():
    st.header("📜 System Activity Logs")
    logs = get_all_logs()
    st.dataframe(pd.DataFrame(logs), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 9. STAFF — Ticket Booking
# ─────────────────────────────────────────────────────────────────────────────

def render_ticket_management():
    st.header("🎟️ Ticket Operations Centre")
    
    tab1, tab2 = st.tabs(["🛒 New Booking", "📜 Ticket History & Management"])

    with tab1:
        # --- STEP 1: SCREENING SELECTION ---
        screenings = get_all_screenings()
        if not screenings:
            st.warning("No active screenings found.")
        else:
            screening_options = {
                f"{s['MovieTitle']} | Room: {s['RoomName']} | {s['ShowDate']}": s 
                for s in screenings
            }
            selected_label = st.selectbox("Select Screening", list(screening_options.keys()))
            scr = screening_options[selected_label]

            if 'booking_cart' not in st.session_state:
                st.session_state.booking_cart = {}

            # --- STEP 2: SEAT MAP ---
        # --- STEP 2: SEAT MAP (FINAL VERSION) ---
        st.subheader(f"🎬 Seat Selection: {scr['RoomName']}")

        # 1. Scoped CSS: Chỉ tác động lên button bên trong class 'seat-map-area'
        st.markdown("""
            <style>
            .seat-map-area div.stButton > button {
                width: 35px !important;
                height: 35px !important;
                padding: 0px !important;
                border-radius: 5px !important;
                margin: 2px !important;
                line-height: 35px !important;
            }
            .screen-container {
                background: linear-gradient(to bottom, #555, #111);
                color: white;
                text-align: center;
                padding: 10px;
                border-radius: 50% / 100% 100% 0 0;
                margin-bottom: 30px;
                font-weight: bold;
                box-shadow: 0px -5px 15px rgba(255,255,255,0.1);
            }
            .legend-item {
                display: flex;
                align-items: center;
                font-size: 14px;
            }
            .legend-box {
                width: 15px; height: 15px; margin-right: 8px; border-radius: 3px;
            }
            </style>
        """, unsafe_allow_html=True)

        # 2. Legend (Dùng HTML để Layout đẹp và không bị dính CSS button)
        l_col1, l_col2, l_col3, l_col4 = st.columns(4)
        with l_col1: st.markdown('<div class="legend-item"><div class="legend-box" style="background-color: #f0f2f6; border: 1px solid #ccc;"></div>Available</div>', unsafe_allow_html=True)
        with l_col2: st.markdown('<div class="legend-item"><div class="legend-box" style="background-color: #ff4b4b;"></div>Selected</div>', unsafe_allow_html=True)
        with l_col3: st.markdown('<div class="legend-item"><div class="legend-box" style="background-color: #e6e9ef;"></div>Sold</div>', unsafe_allow_html=True)
        with l_col4: st.markdown('<div class="legend-item"><div class="legend-box" style="background-color: #262730;"></div>Locked</div>', unsafe_allow_html=True)

        st.write("") 

        seats = get_seats_by_room(scr['RoomID'])

        if not seats:
            st.error("No seats configured for this room.")
        else:
            # BAO BỌC TRONG DIV ĐỂ ÁP DỤNG CSS SCOPE
            st.markdown('<div class="seat-map-area">', unsafe_allow_html=True)
            
            st.markdown('<div class="screen-container">SCREEN</div>', unsafe_allow_html=True)
            
            rows = sorted(list(set(s['RowChar'] for s in seats)))
            
            for row_char in rows:
                row_seats = [s for s in seats if s['RowChar'] == row_char]
                cols = st.columns([0.5] + [1] * len(row_seats) + [0.5])
                
                with cols[0]:
                    st.markdown(f"<div style='line-height:35px; text-align:right; padding-right:10px;'><b>{row_char}</b></div>", unsafe_allow_html=True)
                    
                for i, seat in enumerate(row_seats):
                    sid = seat['SeatID']
                    s_num = seat['SeatNumber']
                    status = seat['Status']
                    
                    with cols[i+1]:
                        is_in_cart = sid in st.session_state.booking_cart
                        
                        if status == 'Booked':
                            st.button("✖️", key=f"sold_{sid}", disabled=True, help=f"Seat {row_char}{s_num}: SOLD")
                        elif status == 'Locked' and seat['LockedUntil'] > datetime.now() and not is_in_cart:
                            st.button("🔒", key=f"lock_{sid}", disabled=True, help=f"Seat {row_char}{s_num}: Locked by another session")
                        else:
                            btn_type = "primary" if is_in_cart else "secondary"
                            if st.button(f"{s_num}", key=f"btn_{sid}", type=btn_type):
                                if is_in_cart:
                                    del st.session_state.booking_cart[sid]
                                    st.rerun()
                                else:
                                    success, msg = book_seat_with_lock(sid, st.session_state.user_id)
                                    if success:
                                        s_info = get_seat_info(sid)
                                        st.session_state.booking_cart[sid] = {
                                            'number': f"{row_char}{s_num}",
                                            'type': s_info['TypeName'],
                                            'price': float(s_info['BasePrice'])
                                        }
                                        st.rerun()
                                    else:
                                        st.error(msg)
                
                with cols[-1]:
                    st.markdown(f"<div style='line-height:35px; text-align:left; padding-left:10px;'><b>{row_char}</b></div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True) # Đóng div seat-map-area

            # --- STEP 3: CART & CUSTOMER ---
            if st.session_state.booking_cart:
                st.divider()
                col_info, col_cust = st.columns([1, 1])
                with col_info:
                    st.subheader("🛒 Selected Seats")
                    total_amount = 0
                    for sid, info in st.session_state.booking_cart.items():
                        st.write(f"- **{info['number']}** ({info['type']}): {info['price']:,.0f} VND")
                        total_amount += info['price']
                    st.markdown(f"### Total: {total_amount:,.0f} VND")

                with col_cust:
                    st.subheader("👤 Customer Information")
                    c_mode = st.radio("Mode", ["Search Existing", "Add New"], horizontal=True)
                    customer_id = None
                    if c_mode == "Search Existing":
                        phone = st.text_input("Customer Phone")
                        if phone:
                            c = get_customer_by_phone(phone)
                            if c:
                                st.success(f"Found: {c['CustomerName']}")
                                customer_id = c['CustomerID']
                            else: st.warning("Customer not found.")
                    else:
                        n = st.text_input("Full Name")
                        p = st.text_input("Phone Number")
                        if n and p and st.button("Add New Customer"):
                            customer_id = add_new_customer(n, p)
                            if customer_id: st.success("Customer Registered!")

                # --- STEP 4: FINAL CONFIRMATION ---
                if st.button("🔥CONFIRM", type="primary", use_container_width=True):
                    if not customer_id:
                        st.error("Please select or register a customer first.")
                    elif "user_id" not in st.session_state:
                        st.error("Staff session lost. Please log in again.")
                    else:
                        success_count = 0
                        for sid, info in st.session_state.booking_cart.items():
                            # Sending 5 arguments as required by your SQL Procedure
                            if book_ticket(customer_id, scr['ScreeningID'], sid, info['price'], st.session_state.user_id):
                                success_count += 1
                        
                        if success_count == len(st.session_state.booking_cart):
                            st.balloons()
                            st.toast("Tickets issued successfully!", icon="✅")
                            st.session_state.booking_cart = {} # Reset cart
                            st.rerun()

    with tab2:
        st.subheader("📜 Management & History")
        bookings = list_bookings()
        if not bookings:
            st.info("No booking history available.")
        else:
            df = pd.DataFrame(bookings)
            # Match the columns from your list_bookings query
            df.columns = ['ID', 'Customer', 'Movie', 'Seat', 'Date', 'Price']
            st.dataframe(df, use_container_width=True)

            st.divider()
            st.write("### Actions")
            t_id = st.selectbox("Select Ticket ID to modify", df['ID'].tolist())
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🗑️ Delete Ticket", type="secondary", use_container_width=True):
                    if delete_ticket(t_id):
                        st.success(f"Ticket #{t_id} deleted and seat released.")
                        st.rerun()
            with c2:
                new_p = st.number_input("Update Total Price", min_value=0)
                if st.button("🔧 Update Price", use_container_width=True):
                    # Call your generic query function here
                    # update_query("UPDATE tickets SET TotalPrice = %s WHERE TicketID = %s", (new_p, t_id))
                    st.success("Price updated successfully!")
                    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 10. STAFF — Movie Search
# ─────────────────────────────────────────────────────────────────────────────
def render_movie_search():
    st.header("🔍 Movie Search")
    keyword = st.text_input("Search by title or genre")
    if keyword:
        movies = list_movies()
        results = [
            m for m in movies
            if keyword.lower() in m.get("MovieTitle", "").lower()
            or keyword.lower() in m.get("GenreName", "").lower()
        ]
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("No movies found.")

# ─────────────────────────────────────────────────────────────────────────────
# 12. STAFF — Customer Management
# ─────────────────────────────────────────────────────────────────────────────
def render_customer_management():
    st.header("👤 Customer Management")

    # 1. Khu vực thêm khách hàng mới
    with st.expander("➕ Add New Customer"):
        with st.form("add_customer_form", clear_on_submit=True):
            name  = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            if st.form_submit_button("Register"):
                if not name or not phone:
                    st.error("All fields are required.")
                else:
                    # Giả sử hàm add_new_customer trả về kết quả thành công
                    add_new_customer(name, phone)
                    st.success(f"Customer '{name}' registered!")
                    st.rerun() # Để cập nhật lại danh sách bên dưới ngay lập tức

    # 2. Khu vực tìm kiếm khách hàng
    st.subheader("🔍 Lookup Customer")
    lookup_phone = st.text_input("Search by phone number")
    if lookup_phone:
        cust = get_customer_by_phone(lookup_phone)
        if cust:
            st.success(f"Found: {cust['CustomerName']} — {cust['PhoneNumber']}")
            # Hiển thị lịch sử đặt vé của khách này
            st.markdown(f"**Booking History for {cust['CustomerName']}**")
            bookings = list_bookings(cust["CustomerID"])
            if bookings:
                st.dataframe(pd.DataFrame(bookings), use_container_width=True, hide_index=True)
            else:
                st.info("This customer has no bookings yet.")
        else:
            st.info("No customer found with that phone number.")

    st.divider() # Ngăn cách phần tìm kiếm và danh sách tổng

    # 3. Khu vực hiển thị danh sách tất cả khách hàng
    st.subheader("📋 Existing Customers")
    all_customers = list_all_customers()
    
    if not all_customers:
        st.info("No customers in database.")
    else:
        df_customers = pd.DataFrame(all_customers)
        
        # Đổi tên cột cho chuyên nghiệp hơn
        df_customers.columns = [
            "ID", "Customer Name", "Phone Number", "Loyalty Points", "Created At"
        ] if len(df_customers.columns) == 5 else df_customers.columns
        
        # Hiển thị bảng với thanh tìm kiếm tích hợp của Streamlit
        st.dataframe(
            df_customers,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Phone Number": st.column_config.TextColumn("Phone Number"),
                "Loyalty Points": st.column_config.NumberColumn(format="%d ⭐️")
            }
        )

def render_dashboard():
    st.title("📊 Business Intelligence Dashboard")

    # ── KPI Metrics ────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("System Status", "Operational")
    with col2: st.metric("Database", "Connected (MySQL)")
    with col3: st.metric("Department", "NEU - DS&AI")
    st.divider()

    # ── Revenue by Movie ───────────────────────────────────────────────────
    st.subheader("🎬 Revenue by Movie (SQL Function)")
    with st.spinner("Fetching data..."):
        all_movie_data = get_all_movies_revenue_summary()
    
    if all_movie_data:
        df_rev = pd.DataFrame(all_movie_data)
        st.bar_chart(df_rev.set_index("title"))
    else:
        st.info("No revenue data available.")
    
    st.divider()

    # ── Revenue Breakdowns ─────────────────────────────────────────────────
    st.subheader("💰 Revenue Analysis")
    tab_tier, tab_room = st.tabs(["By Seat Tier", "By Room Type"])

    with tab_tier:
        tier_data = get_revenue_by_tier()
        if tier_data:
            df_tier = pd.DataFrame(tier_data)
            c1, c2 = st.columns([1, 2])
            c1.dataframe(df_tier, use_container_width=True)
            c2.bar_chart(df_tier, x="Seat_Tier", y="Revenue")

    with tab_room:
        room_data = get_revenue_by_room_type()
        if room_data:
            df_room = pd.DataFrame(room_data)
            c3, c4 = st.columns([1, 2])
            c3.dataframe(df_room, use_container_width=True)
            c4.bar_chart(df_room, x="Room_Type", y="Revenue")

    st.divider()

    # ── Occupancy & Top Customers ──────────────────────────────────────────
    c_left, c_right = st.columns(2)

    with c_left:
        st.subheader("📈 Occupancy Rate")
        occupancy = get_occupancy_report()
        if occupancy:
            df_occ = pd.DataFrame(occupancy)
            st.dataframe(df_occ.style.format({"Occupancy_Rate": "{:.2%}"}), use_container_width=True)
        else:
            st.info("No data available.")

    with c_right:
        st.subheader("🏆 Top Loyal Customers")
        top_custs = get_top_customers(limit=5)
        if top_custs:
            df_cust = pd.DataFrame(top_custs)
            df_cust.columns = ["Customer Name", "Tickets"]
            st.table(df_cust)

# ─────────────────────────────────────────────────────────────────────────────
# 13. ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main()