import pygplates
import numpy as np
import os
from ptt.utils.call_system_command import call_system_command
import xarray as xr
from joblib import Parallel, delayed
import tempfile
import pygmt

import gprm.utils.paleogeography as pg
from gprm.utils.spatial import get_merged_cob_terrane_polygons, get_merged_cob_terrane_raster
from gprm.utils.fileio import write_xyz_file

from . import reconstruct_by_topologies as rbt

import ptt.separate_ridge_transform_segments as separate_ridge_transform_segments

###########################################################
def get_mid_ocean_ridges(shared_boundary_sections,rotation_model,reconstruction_time,sampling=2.0):
    """ Get tessellated points along a mid ocean ridge"""

    shifted_mor_points = []

    for shared_boundary_section in shared_boundary_sections:
        # The shared sub-segments contribute either to the ridges or to the subduction zones.
        if shared_boundary_section.get_feature().get_feature_type() == pygplates.FeatureType.create_gpml('MidOceanRidge'):
            # Ignore zero length segments - they don't have a direction.
            spreading_feature = shared_boundary_section.get_feature()

            # Find the stage rotation of the spreading feature in the frame of reference of its
            # geometry at the current reconstruction time (the MOR is currently actively spreading).
            # The stage pole can then be directly geometrically compared to the *reconstructed* spreading geometry.
            stage_rotation = separate_ridge_transform_segments.get_stage_rotation_for_reconstructed_geometry(
                spreading_feature, rotation_model, reconstruction_time)
            if not stage_rotation:
                # Skip current feature - it's not a spreading feature.
                continue

            # Get the stage pole of the stage rotation.
            # Note that the stage rotation is already in frame of reference of the *reconstructed* geometry at the spreading time.
            stage_pole, _ = stage_rotation.get_euler_pole_and_angle()

            # One way rotates left and the other right, but don't know which - doesn't matter in our example though.
            rotate_slightly_off_mor_one_way = pygplates.FiniteRotation(stage_pole, np.radians(0.01))
            rotate_slightly_off_mor_opposite_way = rotate_slightly_off_mor_one_way.get_inverse()

            # Iterate over the shared sub-segments.
            for shared_sub_segment in shared_boundary_section.get_shared_sub_segments():

                # Tessellate MOR section.
                mor_points = pygplates.MultiPointOnSphere(shared_sub_segment.get_resolved_geometry().to_tessellated(np.radians(sampling)))

                # NOTE temporary hack to avoid seed points at ridge trench intersections
                for point in mor_points.get_points()[1:-1]:
                    # Append shifted geometries (one with points rotated one way and the other rotated the opposite way).
                    shifted_mor_points.append(rotate_slightly_off_mor_one_way * point)
                    shifted_mor_points.append(rotate_slightly_off_mor_opposite_way * point)

    #print shifted_mor_points
    return shifted_mor_points


def get_isochrons_for_ridge_snapshot(topology_features,
                                     rotation_filename,
                                     out_dir,
                                     ridge_time,
                                     time_step,
                                     youngest_seed_time=0,
                                     ridge_sampling=2.
                                    ):
    print("... Writing seed points along a ridge")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    rotation_model = pygplates.RotationModel(rotation_filename)

    oldest_seed_time = ridge_time

    all_longitudes = []
    all_latitudes = []
    all_ages = []

    # The first step is to generate points along the ridge
    resolved_topologies = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(topology_features, rotation_filename, resolved_topologies, oldest_seed_time, shared_boundary_sections)

    # Previous points are on the MOR, current are moved by one time step off MOR.
    curr_points = get_mid_ocean_ridges(shared_boundary_sections, rotation_model, oldest_seed_time, ridge_sampling)

    # Write out the ridge points born at 'ridge_time' but their position shifted by a small amount to allow cookie-cutting'.
    mor_point_features = []
    for curr_point in curr_points:
        feature = pygplates.Feature()
        feature.set_geometry(curr_point)
        feature.set_valid_time(ridge_time, -999)  # delete - time_step
        mor_point_features.append(feature)
    pygplates.FeatureCollection(mor_point_features).write('{:s}/MOR_plus_one_points_{:0.2f}.gmt'.format(out_dir, ridge_time))
    #
    print("... Finished writing seed points along the mid ocean ridge for {:0.2f} Ma".format(ridge_time))


# --- for parallelisation
def get_isochrons_for_ridge_snapshot_parallel_pool_function(args):
    try:
        return get_isochrons_for_ridge_snapshot(*args)
    except KeyboardInterrupt:
        pass


def get_isochrons_for_ridge_snapshot_parallel(topology_features, rotation_filename,
                                              out_dir, pool_ridge_time_list,
                                              time_step, youngest_seed_time=0.,
                                              ridge_sampling=2, num_cpus=1):

    if num_cpus==1:
        for pool_ridge_time in pool_ridge_time_list:
            get_isochrons_for_ridge_snapshot(topology_features, rotation_filename,
                                             out_dir, pool_ridge_time,
                                             time_step, youngest_seed_time, ridge_sampling)
        return

    else:
        Parallel(n_jobs=num_cpus, prefer="threads")(delayed(get_isochrons_for_ridge_snapshot) \
                                  (topology_features, rotation_filename,
                                   out_dir, pool_ridge_time,
                                   time_step, youngest_seed_time, ridge_sampling)
                                  for pool_ridge_time in pool_ridge_time_list)


"""
def merge_features(young_time, old_time, time_step, outdir, cleanup=False):
    # merge the seed points from the 'initial condition' and generated through
    # the reconstructed mid-ocean ridges through time into a single file
    # TODO
    # - why not use gpmlz NO DON'T USE GPML, SERIOUSLY
    # - filenames should not be hard-coded

    merge_features = []

    for time in np.arange(old_time, young_time-time_step, -time_step):
        filename = './{:s}/MOR_plus_one_points_{:0.2f}.gmt'.format(outdir, time)
        print('merging seeds from file {:s}'.format(filename))
        features = pygplates.FeatureCollection(filename)
        for feature in features:
            merge_features.append(feature)

    merge_filename = './{:s}/MOR_plus_one_merge_{:0.2f}_{:0.2f}.gmt'.format(outdir, young_time, old_time)
    print('Attempting to write merged file {:s}'.format(merge_filename))
    pygplates.FeatureCollection(merge_features).write(merge_filename)

    if cleanup:
        # remove old files that are no longer needed
        for f in glob.glob("{:s}/MOR_plus_one_points_*.gmt".format(outdir)):
            os.remove(f)
        for f in glob.glob("{:s}/MOR_plus_one_points_*.gmt.gplates.xml".format(outdir)):
            os.remove(f)
"""

def get_initial_ocean_seeds(topology_features, input_rotation_filenames, COBterrane_file, output_directory,
                            time, initial_ocean_mean_spreading_rate, initial_ocean_healpix_sampling,
                            area_threshold, mask_sampling=0.5):
    # Get a set of points at the oldest time for a reconstruction sequence, such that the points
    # populate the ocean basins (defined using the COB Terrane polygons) and are assigned ages assuming
    # a uniform average spreading rate combined with the distance of each point to the nearest
    # MidOceanRidge feature in the resolved plate boundary of the the plate containing the point

    print('Begin creating seed points for initial ocean at reconstruction start time....')

    rotation_model = pygplates.RotationModel(input_rotation_filenames)

    cobter = get_merged_cob_terrane_polygons(COBterrane_file, rotation_model,time,
                                             mask_sampling, area_threshold)

    ocean_points = pg.rasterise_paleogeography(cobter, rotation_model,time,
                                               sampling=initial_ocean_healpix_sampling, meshtype='healpix',
                                               masking='Inside')
    #ocean_points = rasterise_polygons(cobter, rotation_model,time,
    #                                  sampling=initial_ocean_healpix_sampling, meshtype='healpix',
    #                                  masking='Inside')

    resolved_topologies = []
    shared_boundary_sections = []
    pygplates.resolve_topologies(topology_features, rotation_model, resolved_topologies, time, shared_boundary_sections)

    pX,pY,pZ = pg.find_distance_to_nearest_ridge(resolved_topologies, shared_boundary_sections, ocean_points)

    # divide spreading rate by 2 to use half spreading rate
    pAge = np.array(pZ) / (initial_ocean_mean_spreading_rate/2.)

    initial_ocean_point_features = []

    for point in zip(pX,pY,pAge):

        point_feature = pygplates.Feature()
        point_feature.set_geometry(pygplates.PointOnSphere(point[1], point[0]))

        # note that we add 'time' to the age at the time of computation
        # to get the valid time in Ma
        point_feature.set_valid_time(point[2]+time, -1)
        initial_ocean_point_features.append(point_feature)

    pygplates.FeatureCollection(initial_ocean_point_features).write('{:s}/age_from_distance_to_mor_{:0.2f}Ma.gmt'.format(output_directory,time))

    print('done')


def get_isochrons_from_topologies(topology_features, input_rotation_filenames, output_directory,
                                  max_time, min_time, time_step, ridge_sampling, num_cpus):

    print('Begin generating seed points along mid ocean ridges from {:0.2f} Ma to {:0.2f} Ma at {:0.2f}Myr increments....'.format(max_time, min_time, time_step))

    youngest_seed_time = time_step
    pool_ridge_time_list = np.arange(max_time, min_time-time_step, -time_step)  # times to create gpml files at

    # here, you can optionally specify a different time step for the output file
    # than the computation. Can be useful if you want to generate seed points
    # at every Myr but then make a sparsely sampled version to load into GPlates
    # (in which case, set 'cleanup=False' in the merge call below)
    time_step_for_output_file = time_step

    # Call the main function.
    # The results are saved in individual GMT format files, one per time step,
    # containing point features (loadable into GPlates)
    get_isochrons_for_ridge_snapshot_parallel(topology_features, input_rotation_filenames,
                                              output_directory,
                                              pool_ridge_time_list, time_step,
                                              youngest_seed_time, ridge_sampling, num_cpus)

    # merge the GMT files from different time steps into a single file
    #print 'Merging seed points into one feature collection....'
    #merge_features(min_time, max_time, time_step_for_output_file, output_directory, cleanup=True)

    print('done')



##################################################################################################
# Functions added for pygplates revision32 mods
DEFAULT_COLLISION = pygplates.ReconstructedGeometryTimeSpan.DefaultDeactivatePoints()

class ContinentCollision(pygplates.ReconstructedGeometryTimeSpan.DeactivatePoints):
    def __init__(self,
                 grd_filename_pattern,
                 chain_collision_detection=DEFAULT_COLLISION):
        
        super(ContinentCollision, self).__init__()
        
        self.grd_filename_pattern = grd_filename_pattern
        self.chain_collision_detection = chain_collision_detection
        
        # Load a new grid each time the reconstruction time changes.
        self.grid_time = None
        
        
    def deactivate(self, prev_point, prev_location, prev_time, current_point, current_location, current_time):
        # Implement your deactivation algorithm here...

        # Load the grid for the current time if encountering a new time.
        if current_time != self.grid_time:
            from scipy.interpolate import RegularGridInterpolator
            from gprm.utils.fileio import load_netcdf

            self.grid_time = current_time
            
            # Load a grid that is based on the continent masks, assuming the detect_continents
            # are represented by NaNs
            # The grid is sampled at each point, and in NaN retrurned, the point is set to inactive
            filename = '{:s}'.format(self.grd_filename_pattern.format(current_time))
            #print('Points masked against grid: {0}'.format(filename))
            gridX,gridY,gridZ = load_netcdf(filename)
            self.continent_deletion_count = 0

            self.f = RegularGridInterpolator((gridX,gridY), gridZ.T, method='nearest')

        # interpolate grid, which is one over continents and zero over oceans.
        # if value is >0.5 we deactivate
        #print curr_point
        if self.f([current_point.to_lat_lon()[1], current_point.to_lat_lon()[0]])>0.5:
            #print 'deactivating point within continent'
            self.continent_deletion_count += 1
            # Detected a collision.
            #print('Found point in continent')
            return True
        
        # We didn't find a collision, so ask the chained collision detection if it did (if we have anything chained).
        if self.chain_collision_detection:
            return self.chain_collision_detection.deactivate(prev_point, 
                                                             prev_location, 
                                                             prev_time, 
                                                             current_point, 
                                                             current_location, 
                                                             current_time) 

        return False


###---------------------
def get_time_span(filename, topological_model, id_start, initial_time, 
                  youngest_time=0, time_increment=1, deactivate_points=DEFAULT_COLLISION):
    
    print('Working on file {:s}...'.format(filename))
    seeds = pygplates.FeatureCollection(filename)

    points = [feature.get_geometry().to_lat_lon() for feature in seeds]
    point_begin_times = [feature.get_valid_time()[0] for feature in seeds]
    point_ids = list(range(id_start, id_start+len(points)))

    time_span = topological_model.reconstruct_geometry(points,
                                                       initial_time=initial_time,
                                                       oldest_time=initial_time,
                                                       youngest_time=youngest_time,
                                                       time_increment=time_increment,
                                                       deactivate_points=deactivate_points)
        
    return time_span, initial_time, point_begin_times, point_ids


#########################################################################
def reconstruct_seeds(input_rotation_filenames, topology_features, seedpoints_output_dir,
                      mor_seedpoint_filename, initial_ocean_seedpoint_filename,
                      max_time, min_time, time_step, grd_output_dir,
                      anchor_plate_id=0,
                      subduction_collision_parameters=(5.0, 10.0), 
                      continent_mask_file_pattern=None,
                      backend='v2'):
    """
    For rigid reconstructions, the 'old' reconstruct_by_topologies function will be much faster
    However, deforming models require the 'new' version
    """

    if backend=='v1':
        reconstruct_seeds_v1(input_rotation_filenames, topology_features, seedpoints_output_dir,
                             mor_seedpoint_filename, initial_ocean_seedpoint_filename,
                             max_time, min_time, time_step, grd_output_dir,
                             anchor_plate_id=anchor_plate_id,
                             subduction_collision_parameters=subduction_collision_parameters, 
                             continent_mask_file_pattern=continent_mask_file_pattern)

    elif backend=='v2':
        reconstruct_seeds_v2(input_rotation_filenames, topology_features, seedpoints_output_dir,
                             mor_seedpoint_filename, initial_ocean_seedpoint_filename,
                             max_time, min_time, time_step, grd_output_dir,
                             anchor_plate_id=anchor_plate_id,
                             subduction_collision_parameters=subduction_collision_parameters, 
                             continent_mask_file_pattern=continent_mask_file_pattern)
        
    

def reconstruct_seeds_v2(input_rotation_filenames, topology_features, seedpoints_output_dir,
                      mor_seedpoint_filename, initial_ocean_seedpoint_filename,
                      max_time, min_time, time_step, grd_output_dir,
                      anchor_plate_id=0,
                      subduction_collision_parameters=(5.0, 10.0), 
                      continent_mask_file_pattern=None):

    topological_model = pygplates.TopologicalModel(topology_features,
                                                   input_rotation_filenames,
                                                   anchor_plate_id=anchor_plate_id)

    # specify the collision detection
    default_collision = pygplates.ReconstructedGeometryTimeSpan.DefaultDeactivatePoints(
        #threshold_velocity_delta=0.5
    )

    # specify the collision depending on whether the continent collision is specified
    if continent_mask_file_pattern:
        collision_spec = ContinentCollision(continent_mask_file_pattern, 
                                            default_collision)
    else:
        collision_spec = default_collision

    print('Begin assembling seed points and reconstructing by topologies....')

    id_start = 0

    time_spans = []

    time_span = get_time_span(initial_ocean_seedpoint_filename, 
                              topological_model,
                              id_start, max_time, 
                              youngest_time=min_time, time_increment=time_step,
                              deactivate_points=collision_spec)
    id_start += len(time_span[2])+1
    time_spans.append(time_span)                                          

    # NB Not creating a time span that includes min_time MORs....
    for birth_time in np.arange(max_time,min_time,-time_step):
        
        time_span = get_time_span('{:s}/MOR_plus_one_points_{:0.2f}.gmt'.format(seedpoints_output_dir, birth_time), 
                                  topological_model,
                                  id_start, birth_time, 
                                  youngest_time=min_time, time_increment=time_step,
                                  deactivate_points=collision_spec)
        
        id_start += len(time_span[2])+1
        time_spans.append(time_span)
        

    for export_time in np.arange(max_time,
                                 min_time-time_step,
                                 -time_step):
        
        print('Exporting gridding input for time {:0.1f}...'.format(export_time))
        
        recon_points_at_time = []
        
        for (time_span, time_span_initial_time, point_begin_times, point_ids) in time_spans:
        
            # If the time span only begins at t=X, we don't care about it for any older time
            if time_span_initial_time<export_time:
                continue

            #print('Exporting for time {}Ma, point birth time is {}'.format(export_time,point_begin_times[0]))


            reconstructed_points = time_span.get_geometry_points(export_time, return_inactive_points=True)

            if reconstructed_points:

                recon_points_at_time.extend(([(reconstructed_point.to_lat_lon()[1],
                                                reconstructed_point.to_lat_lon()[0],
                                                point_begin_time-export_time,
                                                point_id) for (reconstructed_point, point_begin_time, point_id) in zip(reconstructed_points,
                                                                                                                    point_begin_times,
                                                                                                                    point_ids) if reconstructed_point is not None]))

        
        write_xyz_file('{:s}/gridding_input/gridding_input_{:0.1f}Ma.xy'.format(grd_output_dir, export_time), recon_points_at_time)


def reconstruct_seeds_v1(input_rotation_filenames, topology_features, seedpoints_output_dir,
                         mor_seedpoint_filename, initial_ocean_seedpoint_filename,
                         max_time, min_time, time_step, grd_output_dir,
                         subduction_collision_parameters=(5.0, 10.0), 
                         anchor_plate_id=None,
                         continent_mask_file_pattern=None):
    # reconstruct the seed points using the reconstruct_by_topologies function
    # returns the result either as lists or dumps to an ascii file

    rotation_model = pygplates.RotationModel(input_rotation_filenames)

    print('Begin assembling seed points and reconstructing by topologies....')

    # load features to reconstruct
    cp = []  # current_point # TODO more verbose names for cp and at
    at = []  # appearance_time
    birth_lat = []  # latitude_of_crust_formation
    prev_lat = []
    prev_lon = []

    seeds_at_start_time = pygplates.FeatureCollection(initial_ocean_seedpoint_filename)
    for feature in seeds_at_start_time:
        cp.append(feature.get_geometry())
        at.append(feature.get_valid_time()[0])
        birth_lat.append(feature.get_geometry().to_lat_lon_list()[0][0])  # Why use a list here??
        prev_lat.append(feature.get_geometry().to_lat_lon_list()[0][0])
        prev_lon.append(feature.get_geometry().to_lat_lon_list()[0][1])

    #seeds_from_topologies = pygplates.FeatureCollection(mor_seedpoint_filename)
    seeds_from_topologies = []

    for time in np.arange(max_time, min_time-time_step, -time_step):
        filename = './{:s}/MOR_plus_one_points_{:0.2f}.gmt'.format(seedpoints_output_dir, time)
        print('merging seeds from file {:s}'.format(filename))
        features = pygplates.FeatureCollection(filename)
        for feature in features:
            seeds_from_topologies.append(feature)

    for feature in seeds_from_topologies:
        if feature.get_valid_time()[0]<max_time:
            cp.append(feature.get_geometry())
            at.append(feature.get_valid_time()[0])
            birth_lat.append(feature.get_geometry().to_lat_lon_list()[0][0])
            prev_lat.append(feature.get_geometry().to_lat_lon_list()[0][0])
            prev_lon.append(feature.get_geometry().to_lat_lon_list()[0][1])

    point_id = range(len(cp))

    # specify the collision detection
    default_collision = rbt.DefaultCollision(feature_specific_collision_parameters = [(pygplates.FeatureType.gpml_subduction_zone, 
                                                                                       subduction_collision_parameters)])
    
    # specify the collision depending on whether the continent collision is specified
    if continent_mask_file_pattern:
        collision_spec = rbt.ContinentCollision(continent_mask_file_pattern, 
                                                default_collision)
    else:
        collision_spec = default_collision

    print('preparing reconstruction by topologies....')
    topology_reconstruction = rbt.ReconstructByTopologies(
            rotation_model, topology_features,
            max_time, min_time, time_step,
            cp, point_begin_times=at,
            detect_collisions = collision_spec)


    # Initialise the reconstruction.
    topology_reconstruction.begin_reconstruction()

    # Loop over the reconstruction times until reached end of the reconstruction time span, or
    # all points have entered their valid time range *and* either exited their time range or
    # have been deactivated (subducted forward in time or consumed by MOR backward in time).
    while True:
        print('reconstruct by topologies: working on time {:0.2f} Ma'.format(topology_reconstruction.get_current_time()))

        curr_points = topology_reconstruction.get_active_current_points()

        curr_lat_lon_points = [point.to_lat_lon() for point in curr_points]
        if curr_lat_lon_points:
            curr_latitudes, curr_longitudes = zip(*curr_lat_lon_points)

            seafloor_age = []
            birth_lat_snapshot = []
            point_id_snapshot = []
            prev_lat_snapshot = []
            prev_lon_snapshot = []
            for point_index,current_point in enumerate(topology_reconstruction.get_all_current_points()):
                if current_point is not None:
                    #all_birth_ages.append(at[point_index])
                    seafloor_age.append(at[point_index] - topology_reconstruction.get_current_time())
                    birth_lat_snapshot.append(birth_lat[point_index])
                    point_id_snapshot.append(point_id[point_index])
                    prev_lat_snapshot.append(prev_lat[point_index])
                    prev_lon_snapshot.append(prev_lon[point_index])
                    
                    prev_lat[point_index] = current_point.to_lat_lon()[0]
                    prev_lon[point_index] = current_point.to_lat_lon()[1]


            write_xyz_file('{:s}/gridding_input/gridding_input_{:0.1f}Ma.xy'.format(grd_output_dir,
                                                                     topology_reconstruction.get_current_time()),
                           zip(curr_longitudes,
                           curr_latitudes,
                           seafloor_age,
                           birth_lat_snapshot,
                           point_id_snapshot))


        if not topology_reconstruction.reconstruct_to_next_time():
            break

    print('done')
    return



##################################################################
# Gridding
def make_grid_for_reconstruction_time(raw_point_file, age_grid_time, grdspace, region,
                                      output_dir, output_filename_template='seafloor_age_',
                                      GridColumnFlag=2):
    """
    given a set of reconstructed points with ages, makes a global grid using
    blockmedian and sphinterpolate
    """

    block_median_points = tempfile.NamedTemporaryFile(delete=False)
    block_median_points.close()  # Cannot open twice on Windows - close before opening again.
    
    region = '{:0.6f}/{:0.6f}/{:0.6f}/{:0.6f}'.format(*region)

    call_system_command(['gmt',
                         'blockmedian',
                         raw_point_file,
                         '-I{0}d'.format(grdspace),
                         '-R{0}'.format(region),
                         '-V',
                         '-i0,1,{0}'.format(GridColumnFlag),
                         '>',
                         block_median_points.name])

    call_system_command(['gmt',
                         'sphinterpolate',
                         block_median_points.name,
                         '-G{0}/unmasked/{1}{2}Ma.nc'.format(output_dir, output_filename_template, age_grid_time),
                         '-I{0}d'.format(grdspace),
                         '-R{0}'.format(region),
                         '-V'])

    os.unlink(block_median_points.name)  # Remove temp file (because we set 'delete=False').


def write_synthetic_points(all_longitudes, all_latitudes, all_birth_ages, all_reconstruction_ages,
                           reconstruction_time, raw_point_file):
    """
    writes an ascii file that contains the points to be input to make an age grid
    at one reconstruction time snapshot.
    """

    # we need the age of each point at the time of the reconstruction, which
    # is the age of birth minus the reconstruction time
    ages_at_reconstruction_time = np.array(all_birth_ages)-np.array(all_reconstruction_ages)

    # create an index that isolates the points valid for this reconstruction time
    index = np.equal(np.array(all_reconstruction_ages), reconstruction_time)

    write_xyz_file(raw_point_file.name,zip(np.array(all_longitudes)[index],
                                      np.array(all_latitudes)[index],
                                      ages_at_reconstruction_time[index]))


def mask_synthetic_points(reconstructed_present_day_lons, reconstructed_present_day_lats,
                          reconstructed_present_day_ages, raw_point_file,
                          grdspace, region, buffer_distance_degrees=1):
    # given an existing ascii file contain only synthetic points at a given reconstruction time,
    # and arrays defining points from the reconstructed present day age grid at this same time,
    # --> create a mask to remove the synthetic points in the area of overlap (+ some buffer)
    # --> apply the mask to remove the overlapping points
    # --> concatentate the remaining synthetic points with the reconstructed present-day age grid points

    reconstructed_present_day_age_file = tempfile.NamedTemporaryFile(delete=False)
    synthetic_age_masked_file = tempfile.NamedTemporaryFile(delete=False)
    masking_grid_file = tempfile.NamedTemporaryFile(delete=False)

    # Cannot open twice on Windows - close before opening again.
    reconstructed_present_day_age_file.close()
    synthetic_age_masked_file.close()
    masking_grid_file.close()

    write_xyz_file(reconstructed_present_day_age_file.name, zip(reconstructed_present_day_lons,
                                                                reconstructed_present_day_lats,
                                                                reconstructed_present_day_ages))

    call_system_command(['gmt',
                         'grdmask',
                         reconstructed_present_day_age_file.name,
                         '-G%s' % masking_grid_file.name,
                         '-I{0}d'.format(grdspace),
                         '-R{0}'.format(region),
                         '-S%0.6fd' % buffer_distance_degrees,
                         '-V'])

    call_system_command(['gmt',
                         'gmtselect',
                         raw_point_file.name,
                         '-G%s' % masking_grid_file.name,
                         '-Ig',
                         '>',
                         synthetic_age_masked_file.name])

    # concatenate the files in a cross-platform way - overwriting the file that contains unmasked synthetic points
    with open(raw_point_file.name, 'w') as outfile:
        for fname in [synthetic_age_masked_file.name,reconstructed_present_day_age_file.name]:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)

    # Remove temp file (because we set 'delete=False').
    os.unlink(reconstructed_present_day_age_file.name)
    os.unlink(synthetic_age_masked_file.name)
    os.unlink(masking_grid_file.name)


def make_masking_grids(COBterrane_file, input_rotation_filenames, max_time, min_time, time_step,
                       grdspace, grd_output_dir, output_gridfile_template, 
                       num_cpus=1):
    # generate the binary masking grids to define which areas are oceanic and which continental

    time_list = np.arange(max_time, min_time-time_step, -time_step)

    Parallel(n_jobs=num_cpus, prefer="threads")(delayed(make_masks_job) \
                                (reconstruction_time, COBterrane_file, input_rotation_filenames, 
                                grdspace, grd_output_dir) \
                                for reconstruction_time in time_list)


def make_grids_from_reconstructed_seeds(input_rotation_filenames, max_time, min_time, time_step,
                                        grdspace, region, grd_output_dir, output_gridfile_template,
                                        num_cpus=1, COBterrane_file=None, GridColumnFlag=2):

    # given sets of reconstructed seed points, generates age grids for a series of
    # reconstruction times
    # optionally:
    # 1. merge with present-day reconstructed age grid
    # 2. mask using COB Terranes (or any reconstructable polygon file)

    #rotation_model = pygplates.RotationModel(input_rotation_filenames)

    time_list = np.arange(max_time, min_time-time_step, -time_step)

    print('Begin Gridding....')
    if num_cpus>1:
        print('Running on {:d} cpus...'.format(num_cpus))
        Parallel(n_jobs=num_cpus, backend="threading")(delayed(gridding_job) \
                                  (input_rotation_filenames, reconstruction_time,
                                   grdspace, region, grd_output_dir, output_gridfile_template,
                                   GridColumnFlag) \
                                  for reconstruction_time in time_list)

    else:
        for reconstruction_time in time_list:
            gridding_job(input_rotation_filenames, reconstruction_time,
                         grdspace, region, grd_output_dir, output_gridfile_template,
                         GridColumnFlag)


    print('done')
    print('Results saved in directory {:s}'.format(grd_output_dir))

    if COBterrane_file is not None:
        for reconstruction_time in time_list:
            masking_job(reconstruction_time, region, grd_output_dir, output_gridfile_template)

    print('All done')

#########################################################################



# Parallelisation Functions
#########################################################################
def gridding_job(input_rotation_filenames, reconstruction_time,
                 grdspace, region, grd_output_dir, output_gridfile_template,
                 GridColumnFlag=2):

    print('Gridding for time {:0.2f} Ma'.format(reconstruction_time))
    raw_point_file = '{:s}/gridding_input/gridding_input_{:0.1f}Ma.xy'.format(grd_output_dir,
                                                                              reconstruction_time)
    make_grid_for_reconstruction_time(raw_point_file, reconstruction_time, grdspace, region,
                                        grd_output_dir, output_gridfile_template, GridColumnFlag)
    return


def masking_job(reconstruction_time, region,
                grd_output_dir, output_gridfile_template='seafloor_age_'):

    #rotation_model = pygplates.RotationModel(input_rotation_filenames)
    print('Masking for time {:0.2f} Ma'.format(reconstruction_time))
    #mask = pt.get_merged_cob_terrane_raster(COBterrane_file, rotation_model, reconstruction_time,
    #                                        grdspace)

    #maskX,maskY,mask = load_netcdf('{0}/masks/mask_{1}Ma.nc'.format(grd_output_dir, reconstruction_time))
    # TODO 
    # the region of the output grid may not match the region of the masks (which are always global)
    # Need to handle this mismatch

    if np.array_equal(region, [-180, 180, -90, 90]):
        mask = xr.open_dataarray('{0}/masks/mask_{1}Ma.nc'.format(grd_output_dir, reconstruction_time))
    else:
        mask = pygmt.grdsample('{0}/masks/mask_{1}Ma.nc'.format(grd_output_dir, reconstruction_time), 
                               region=region)

    ds = xr.open_dataarray('{0}/unmasked/{1}{2}Ma.nc'.format(grd_output_dir, output_gridfile_template, reconstruction_time))

    # workaround for a bug in older versions of xarray, where masking array cannot be applied directly to data array
    #ds['z'][mask==1] = np.nan
    z_array = ds.data
    z_array[mask.data==1] = np.nan
    ds.data = z_array
    ds.to_netcdf('{0}/masked/{1}mask_{2}Ma.nc'.format(grd_output_dir, output_gridfile_template, reconstruction_time),
                 format='NETCDF4_CLASSIC')
    ds.close()

    return

def make_masks_job(reconstruction_time, COBterrane_file, input_rotation_filenames,
                   grdspace, grd_output_dir):

    rotation_model = pygplates.RotationModel(input_rotation_filenames)
    print('Masking for time {:0.2f} Ma'.format(reconstruction_time))
    mask = get_merged_cob_terrane_raster(COBterrane_file, rotation_model, reconstruction_time,
                                         grdspace, method='rasterio')

    gridX = np.arange(-180.,180.+grdspace,grdspace)
    gridY = np.arange(-90.,90.+grdspace,grdspace)
    #write_netcdf_grid('{0}/masks/mask_{1}Ma.nc'.format(grd_output_dir, reconstruction_time),
    #                  gridX, gridY, mask.astype(int))

    ds = xr.DataArray(mask, coords=[('y',gridY), ('x',gridX)], name='z')
    ds.to_netcdf('{0}/masks/mask_{1}Ma.nc'.format(grd_output_dir, reconstruction_time),
                 format='NETCDF4_CLASSIC', encoding={'z': {'dtype': 'int16'}})
    ds.close()
    return
