from pydrake.visualization import (
    ModelVisualizer
)

package_path = "./roboball_plant/RoboBall_URDF/package.xml"
robot_file = "./roboball_plant/RoboBall_URDF/urdf/RoboBall_URDF.urdf"

modelViz = ModelVisualizer(visualize_frames=True, triad_length=1)

pkg_mp = modelViz.package_map()
pkg_mp.AddPackageXml(package_path)

modelViz.AddModels(robot_file)
modelViz.Run()