import streamlit as st
import pandas as pd
import os
from pathlib import Path

# set the title of the app
st.title('3D Object Labeling App')

if 'running' not in st.session_state:
    st.session_state.running = False

if not st.session_state.running:
    # start button
    if st.button('Start'):
        st.session_state.running = True

if not st.session_state.running:
    # label_objaverse as a toggle switch
    st.session_state.label_objaverse = st.toggle('Label Objaverse(True) or Shapenet(False)', value=True)

    # Base path for the dataset
    st.write("Please provide a path which points to the rendered image folders for the dataset you want to label.")
    st.session_state.datset_base_path = st.text_input(
        'Dataset Base Path', value="/Users/damian/Datasets/objaverse/renders/")

def load_votes_file(votes_path):
    if os.path.exists(votes_path):
        existing_votes_df = pd.read_csv(votes_path)
    else:
        existing_votes_df = pd.DataFrame(columns=['uid', 'vote'])
    return existing_votes_df

# Function to save votes
def save_votes(uid, vote):
    global existing_votes_df
    if uid in existing_votes_df['uid'].values:
        existing_votes_df.loc[existing_votes_df['uid'] == uid, 'vote'] = vote
    else:
        new_vote = pd.DataFrame({'uid': [uid], 'vote': [vote]})
        existing_votes_df = pd.concat(
            [existing_votes_df, new_vote], ignore_index=True)
    existing_votes_df.to_csv(votes_path, index=False)

# Function to display next object
def next_object():
    if st.session_state.current_index < len(df) - 1:
        st.session_state.current_index += 1

# Function to display previous object
def prev_object():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1

# Function to set the current index
def set_current_index(index):
    if 0 <= index < len(df):
        st.session_state.current_index = index

# Function to get renders
def get_renders(uid):
    base_path = Path(rendered_images_base_path)
    render_path = base_path / f'{uid}'
    if render_path.exists() and render_path.is_dir():
        image_list = []
        for image_name in os.listdir(render_path):
            if image_name.endswith('.png'):
                whole_path = render_path / image_name
                image_list.append(whole_path)
        return image_list
    return []

# start the app
if st.session_state.running:
    if st.session_state.label_objaverse:
        # Path to the rendered images
        rendered_images_base_path = st.session_state.datset_base_path # + "/objaverse/renders"
        # Path to the votes file
        votes_path = './car_quality_votes_objaverse.csv'
        # dataframe with uids we want to label
        df = pd.read_csv('./car_label_uids_objaverse.csv')

        # make toggle switch to show/hide the thumbnail
        show_thumbnail = st.sidebar.toggle('Show Thumbnail', value=False)

        # Load existing votes
        existing_votes_df = load_votes_file(votes_path)
    else:
        # Path to the rendered images
        rendered_images_base_path = st.session_state.datset_base_path # + "/shapenet/renders"
        # Path to the votes file
        votes_path = './car_quality_votes_shapenet.csv'
        # dataframe with uids we want to label
        df = pd.read_csv('./car_label_uids_shapenet.csv')

        # Load existing votes
        existing_votes_df = load_votes_file(votes_path)

    # Initialize session state
    if 'current_index' not in st.session_state:
        if not existing_votes_df.empty:
            last_voted_uid = existing_votes_df.iloc[-1]['uid']
            st.session_state.current_index = df.index[df['uid'] == last_voted_uid].tolist()[
                0] + 1
        else:
            st.session_state.current_index = 0
    if 'votes' not in st.session_state:
        st.session_state.votes = []

    # Display object info
    current_obj = df.iloc[st.session_state.current_index]
    st.write(
        f"Object {st.session_state.current_index + 1} / {len(df)} - UID: {current_obj['uid']}")

    if st.session_state.label_objaverse:
        # show the name of the car
        st.write(current_obj['name'])
        if show_thumbnail:
            st.image(current_obj['thumbnail_url'], caption=current_obj['name'])

    # Display renders if they exist
    renders = get_renders(current_obj['uid'])
    if renders:
        cols = st.columns(2)
        for i, render in enumerate(renders):
            cols[i % 2].image(str(render))
    else:
        st.write("No renders found")

    # Check if current object already has a vote
    current_vote = existing_votes_df[existing_votes_df['uid']
                                    == current_obj['uid']]
    if not current_vote.empty:
        st.write(f"Current vote: {current_vote.iloc[0]['vote']}")
    else:
        st.write("No vote yet")

    # Voting buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button('1-Bad', key='1-Bad', help="1-Bad"):
            st.session_state.votes.append((current_obj['uid'], '1'))
            save_votes(current_obj['uid'], '1')
            next_object()
            st.rerun()
    with col2:
        if st.button('2-MB', key='2-MB', help="2-MB"):
            st.session_state.votes.append((current_obj['uid'], '2'))
            save_votes(current_obj['uid'], '2')
            next_object()
            st.rerun()
    with col3:
        if st.button('3-Medium', key='3-Medium', help="3-Medium"):
            st.session_state.votes.append((current_obj['uid'], '3'))
            save_votes(current_obj['uid'], '3')
            next_object()
            st.rerun()
    with col4:
        if st.button('4-MG', key='4-MG', help="4-MG"):
            st.session_state.votes.append((current_obj['uid'], '4'))
            save_votes(current_obj['uid'], '4')
            next_object()
            st.rerun()
    with col5:
        if st.button('5-Good', key='5-Good', help="5-Good"):
            st.session_state.votes.append((current_obj['uid'], '5'))
            save_votes(current_obj['uid'], '5')
            next_object()
            st.rerun()

    # Display current votes count
    st.write(f"Votes: {len(st.session_state.votes)}")

    # draw a line
    st.divider()

    # Navigation buttons
    st.write("Navigation")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('Previous'):
            prev_object()
            st.rerun()
    with col2:
        if st.button('Reload Thumbnail'):
            st.rerun()
    with col3:
        if st.button('Next'):
            next_object()
            st.rerun()

    # draw a line
    st.divider()

    # Textbox to set current index
    st.write("Go to object")
    index_input = st.text_input("Enter object number:", "")
    if st.button("Go to object"):
        try:
            index = int(index_input) - 1
            set_current_index(index)
            st.rerun()
        except ValueError:
            st.write("Please enter a valid number.")

    if st.session_state.label_objaverse:
        # draw a line
        st.divider()

        # Checkbox to load embedding
        st.write("Sketchfab Embedding")
        load_embedding = st.checkbox('Load Embedding')

        # Display Sketchfab embedding if checkbox is selected
        if load_embedding:
            embed_url = current_obj['embedUrl']
            st.markdown(
                f'<iframe src="{embed_url}" width="640" height="480" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)


