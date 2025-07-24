import streamlit as st
import cadquery as cq
import tempfile
import os

# Function to simulate 3D model creation from an uploaded 2D image
def create_3d_module_from_image(dims=(30,30,30), magnet_diameter=5, magnet_depth=3):
    # For demonstration: create a cube and add a magnet hole on one face
    size_x, size_y, size_z = dims
    module = (
        cq.Workplane("XY")
        .box(size_x, size_y, size_z)
        .faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .hole(magnet_diameter, magnet_depth)
    )
    return module

# Function to split the module into two interlocking parts along the Z axis
def split_module(module, split_at=15, peg_diameter=4, peg_length=6):
    # Create the two halves split at split_at along Z axis
    # Cut the cube into bottom and top parts
    lower_half = module.cut(
        cq.Workplane("XY").box(100, 100, 100).translate((0, 0, split_at + 50))
    ).intersect(
        cq.Workplane("XY").box(100, 100, 2*split_at).translate((0, 0, split_at/2))
    )
    upper_half = module.cut(
        cq.Workplane("XY").box(100, 100, 2*split_at).translate((0, 0, split_at/2))
    ).intersect(
        cq.Workplane("XY").box(100, 100, 100).translate((0, 0, split_at + 50))
    )

    # Add a peg to the lower half, and hole for peg in upper half (interlocking)
    peg = (
        cq.Workplane("XY")
        .circle(peg_diameter / 2)
        .extrude(peg_length)
        .translate((0, 0, split_at))
    )

    lower_half = lower_half.union(peg)
    upper_half = upper_half.cut(peg)

    # Add magnet holes in both halves (simplified)
    magnet_hole_pos = (size_x/4, size_y/4)
    for half in [lower_half, upper_half]:
        half.faces(">Z").workplane().center(*magnet_hole_pos).hole(5, 3)

    return lower_half, upper_half

# Function to export CadQuery objects to STL and return file paths
def export_stl_modules(modules, prefixes=["module1", "module2"]):
    paths = []
    for mod, prefix in zip(modules, prefixes):
        fd, path = tempfile.mkstemp(suffix=".stl", prefix=prefix)
        os.close(fd)
        cq.exporters.export(mod, path)
        paths.append(path)
    return paths

################ Streamlit UI ################

st.title("2D Image to Interlockable 3D Modules Prototype")

uploaded_file = st.file_uploader("Upload a 2D image (PNG, JPG)", type=["png","jpg","jpeg"])

size_x = st.slider("Module Size X (mm)", 10, 100, 30)
size_y = st.slider("Module Size Y (mm)", 10, 100, 30)
size_z = st.slider("Module Size Z (mm)", 5, 60, 30)

magnet_diameter = st.slider("Magnet Diameter (mm)", 2, 10, 5)
magnet_depth = st.slider("Magnet Depth (mm)", 1, 10, 3)

peg_diameter = st.slider("Peg Diameter (mm)", 2, 10, 4)
peg_length = st.slider("Peg Length (mm)", 1, 15, 6)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Placeholder: Use the image to create a simple cube-based module (simulate AI 2D-to-3D)
    with st.spinner("Generating 3D module from image..."):
        base_module = create_3d_module_from_image(
            dims=(size_x, size_y, size_z),
            magnet_diameter=magnet_diameter,
            magnet_depth=magnet_depth,
        )

    st.success("3D module created!")

    # Split the module into interlocking parts
    with st.spinner("Creating interlockable parts..."):
        lower_half, upper_half = split_module(
            base_module,
            split_at=size_z / 2,
            peg_diameter=peg_diameter,
            peg_length=peg_length,
        )
    st.success("Interlocking parts created!")

    # Export parts to STL
    st.write("Exporting STL files...")
    stl_paths = export_stl_modules([lower_half, upper_half])

    # Provide download buttons
    for i, path in enumerate(stl_paths):
        with open(path, "rb") as f:
            st.download_button(
                label=f"Download STL for Module Part {i+1}",
                data=f,
                file_name=os.path.basename(path),
                mime="application/octet-stream",
            )

    st.caption(
        "Note: This is a simplified demonstration. Replace the 'create_3d_module_from_image' with your actual 2D->3D AI model integration."
    )
else:
    st.info("Please upload a 2D image to start.")

