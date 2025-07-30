// Copyright 2024 Mikael Lund
//
// Licensed under the Apache license, version 2.0 (the "license");
// you may not use this file except in compliance with the license.
// You may obtain a copy of the license at
//
//     http://www.apache.org/licenses/license-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the license is distributed on an "as is" basis,
// without warranties or conditions of any kind, either express or implied.
// See the license for the specific language governing permissions and
// limitations under the license.

use anyhow::{bail, Result};
use clap::{Parser, Subcommand};
use coulomb::{permittivity, DebyeLength, Medium, Salt, Vector3};
use duello::{
    energy, icoscan,
    icotable::IcoTable2D,
    structure::{pqr_write_atom, Structure},
    SphericalCoord, UnitQuaternion,
};
use faunus::{energy::NonbondedMatrix, topology::Topology};
use std::process::ExitCode;
use std::{f64::consts::PI, fs::File, io::Write, ops::Add, ops::Neg, path::PathBuf};
extern crate pretty_env_logger;
#[macro_use]
extern crate log;
use iter_num_tools::arange;
use rand::Rng;

#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    Dipole {
        /// Path to first XYZ file
        #[arg(short = 'o', long)]
        output: PathBuf,
        /// Dipole moment strength
        #[arg(short = 'm')]
        mu: f64,
        /// Angular resolution in radians
        #[arg(short = 'r', long, default_value = "0.1")]
        resolution: f64,
        /// Minimum mass center distance
        #[arg(long)]
        rmin: f64,
        /// Maximum mass center distance
        #[arg(long)]
        rmax: f64,
        /// Mass center distance step
        #[arg(long)]
        dr: f64,
    },

    Potential {
        /// Path to first XYZ file
        #[arg(short = '1', long)]
        mol1: PathBuf,
        /// Angular resolution in radians
        #[arg(short = 'r', long, default_value = "0.1")]
        resolution: f64,
        /// Radius around center of mass to scan to calc. potentil (angstroms)
        #[arg(long)]
        radius: f64,
        /// YAML file with atom definitions (names, charges, etc.)
        #[arg(short = 'p', long = "top")]
        topology: PathBuf,
        /// 1:1 salt molarity in mol/l
        #[arg(short = 'M', long, default_value = "0.1")]
        molarity: f64,
        /// Cutoff distance for pair-wise interactions (angstroms)
        #[arg(long, default_value = "50.0")]
        cutoff: f64,
        /// Temperature in K
        #[arg(short = 'T', long, default_value = "298.15")]
        temperature: f64,
    },

    /// Scan angles and tabulate energy between two rigid bodies
    Scan {
        /// Path to first XYZ file
        #[arg(short = '1', long)]
        mol1: PathBuf,
        /// Path to second XYZ file
        #[arg(short = '2', long)]
        mol2: PathBuf,
        /// Angular resolution in radians
        #[arg(short = 'r', long, default_value = "0.1")]
        resolution: f64,
        /// Minimum mass center distance
        #[arg(long)]
        rmin: f64,
        /// Maximum mass center distance
        #[arg(long)]
        rmax: f64,
        /// Mass center distance step
        #[arg(long)]
        dr: f64,
        /// YAML file with atom definitions (names, charges, etc.)
        #[arg(short = 'a', long = "top")]
        topology: PathBuf,
        /// 1:1 salt molarity in mol/l
        #[arg(short = 'M', long, default_value = "0.1")]
        molarity: f64,
        /// Cutoff distance for pair-wise interactions (angstroms)
        #[arg(long, default_value = "50.0")]
        cutoff: f64,
        /// Temperature in K
        #[arg(short = 'T', long, default_value = "298.15")]
        temperature: f64,
        /// Optionally use fixed dielectric constant
        #[arg(long)]
        fixed_dielectric: Option<f64>,
        /// Output file for PMF
        #[arg(long = "pmf", default_value = "pmf.dat")]
        pmf_file: PathBuf,
        /// Save table to disk (use .gz suffix for compression)
        #[arg(long)]
        savetable: Option<PathBuf>,
        /// Export XTC file with all poses
        #[arg(long)]
        xtcfile: Option<PathBuf>,
    },
}

/// Calculate energy of all two-body poses
fn do_scan(cmd: &Commands) -> Result<()> {
    let Commands::Scan {
        mol1,
        mol2,
        resolution,
        rmin,
        rmax,
        dr,
        topology: top_file,
        molarity,
        cutoff,
        temperature,
        fixed_dielectric,
        pmf_file,
        savetable,
        xtcfile,
    } = cmd
    else {
        bail!("Unknown command");
    };
    assert!(rmin < rmax);

    let mut topology = Topology::from_file_partial(top_file)?;
    topology.finalize_atoms()?;
    topology.finalize_molecules()?;
    faunus::topology::set_missing_epsilon(topology.atomkinds_mut(), 2.479);

    // Either use fixed dielectric constant or calculate it from the medium
    let medium = match fixed_dielectric {
        Some(dielectric_const) => Medium::new(
            *temperature,
            permittivity::Permittivity::Fixed(*dielectric_const),
            Some((Salt::SodiumChloride, *molarity)),
        ),
        _ => Medium::salt_water(*temperature, Salt::SodiumChloride, *molarity),
    };

    let multipole = coulomb::pairwise::Plain::new(*cutoff, medium.debye_length());
    let nonbonded = NonbondedMatrix::from_file(top_file, &topology, Some(medium.clone()))?;
    let pair_matrix = energy::PairMatrix::new_with_coulomb(
        nonbonded,
        topology.atomkinds(),
        medium.permittivity().into(),
        &multipole,
    );
    let ref_a = Structure::from_xyz(mol1, topology.atomkinds())?;
    let ref_b = Structure::from_xyz(mol2, topology.atomkinds())?;
    if xtcfile.is_some() {
        log::info!("Exporting merged XYZ file with both initial structures: confout.xyz");
        ref_a
            .clone()
            .add(ref_b.clone())
            .to_xyz(&mut File::create("confout.xyz")?, topology.atomkinds())?;
    }

    info!("{}", medium);
    info!(
        "Molecular net-charges:    [{:.2}e, {:.2}e]",
        ref_a.net_charge(),
        ref_b.net_charge(),
    );

    const ELECTRON_ANGSTROM_TO_DEBYE: f64 = 4.80320425;
    info! {
        "Molecular dipole moments: [{:.2} D, {:.2} D]",
        ref_a.dipole_moment().norm() * ELECTRON_ANGSTROM_TO_DEBYE,
        ref_b.dipole_moment().norm() * ELECTRON_ANGSTROM_TO_DEBYE,
    };

    info!(
        "Molecular masses (g/mol): [{:.2}, {:.2}]",
        ref_a.total_mass(),
        ref_b.total_mass(),
    );

    info!(
        "COM range: [{:.1}, {:.1}) in {:.1} Å steps 🐾",
        rmin, rmax, dr
    );
    icoscan::do_icoscan(
        *rmin,
        *rmax,
        *dr,
        *resolution,
        ref_a,
        ref_b,
        pair_matrix,
        temperature,
        pmf_file,
        savetable,
        xtcfile,
    )
}

fn do_dipole(cmd: &Commands) -> Result<()> {
    let Commands::Dipole {
        output,
        mu: dipole_moment,
        resolution,
        rmin,
        rmax,
        dr,
    } = cmd
    else {
        panic!("Unexpected command");
    };
    let distances: Vec<f64> = iter_num_tools::arange(*rmin..*rmax, *dr).collect();
    let n_points = (4.0 * PI / resolution.powi(2)).round() as usize;
    let mut icotable = IcoTable2D::<f64>::from_min_points(n_points)?;
    let resolution = (4.0 * PI / icotable.len() as f64).sqrt();
    log::info!(
        "Requested {} points on a sphere; got {} -> new resolution = {:.3}",
        n_points,
        icotable.len(),
        resolution
    );

    let mut dipole_file = File::create(output)?;
    writeln!(dipole_file, "# R/Å w_vertex w_exact w_interpolated")?;

    let charge = 1.0;
    let bjerrum_len = 7.0;

    // for each ion-dipole separation, calculate the partition function and free energy
    for radius in distances {
        // exact exp. energy at a given point, exp(-βu)
        let exact_exp_energy = |_, p: &Vector3| {
            let (_r, theta, _phi) = SphericalCoord::from_cartesian(*p).into();
            let field = bjerrum_len * charge / radius.powi(2);
            let energy_in_kt = field * dipole_moment * theta.cos();
            energy_in_kt.neg().exp()
        };
        icotable.clear_vertex_data();
        icotable.set_vertex_data(exact_exp_energy)?;

        // Q summed from exact data at each vertex
        let partition_function = icotable.vertex_data().sum::<f64>() / icotable.len() as f64;

        // analytical solution to angular average of exp(-βu)
        let field = -bjerrum_len * charge / radius.powi(2);
        let exact_free_energy = ((field * dipole_moment).sinh() / (field * dipole_moment))
            .ln()
            .neg();

        // rotations to apply to vertices of a new icosphere used for sampling interpolated points
        let mut rng = rand::thread_rng();
        let quaternions: Vec<UnitQuaternion> = (0..20)
            .map(|_| {
                let point = faunus::transform::random_unit_vector(&mut rng);
                UnitQuaternion::from_axis_angle(
                    &nalgebra::Unit::new_normalize(point),
                    rng.gen_range(0.0..PI),
                )
            })
            .collect();

        // Sample interpolated points using a randomly rotate icospheres
        let mut rotated_icosphere = IcoTable2D::<f64>::from_min_points(1000)?;
        let mut partition_func_interpolated = 0.0;

        for q in &quaternions {
            rotated_icosphere.transform_vertex_positions(|v| q.transform_vector(v));
            partition_func_interpolated += rotated_icosphere
                .iter()
                .map(|(pos, _, _)| icotable.interpolate(pos))
                .sum::<f64>()
                / rotated_icosphere.len() as f64;
        }
        partition_func_interpolated /= quaternions.len() as f64;

        writeln!(
            dipole_file,
            "{:.5} {:.5} {:.5} {:.5}",
            radius,
            partition_function.ln().neg(),
            exact_free_energy,
            partition_func_interpolated.ln().neg(),
        )?;
    }
    Ok(())
}

// Calculate electric potential at points on a sphere around a molecule
fn do_potential(cmd: &Commands) -> Result<()> {
    let Commands::Potential {
        mol1,
        resolution,
        radius,
        topology,
        molarity,
        cutoff,
        temperature,
    } = cmd
    else {
        panic!("Unexpected command");
    };
    let mut topology = Topology::from_file_partial(topology)?;
    faunus::topology::set_missing_epsilon(topology.atomkinds_mut(), 2.479);

    let structure = Structure::from_xyz(mol1, topology.atomkinds())?;

    let n_points = (4.0 * PI / resolution.powi(2)).round() as usize;
    let vertices = duello::make_icosphere_vertices(n_points)?;
    let resolution = (4.0 * PI / vertices.len() as f64).sqrt();
    log::info!(
        "Requested {} points on a sphere; got {} -> new resolution = {:.2}",
        n_points,
        vertices.len(),
        resolution
    );

    // Electrolyte background
    let medium = Medium::salt_water(*temperature, Salt::SodiumChloride, *molarity);
    let multipole = coulomb::pairwise::Plain::new(*cutoff, medium.debye_length());

    let icotable = IcoTable2D::<f64>::from_min_points(n_points)?;
    icotable.set_vertex_data(|_, v| {
        energy::electric_potential(&structure, &v.scale(*radius), &multipole)
    })?;

    File::create("pot_at_vertices.dat")?.write_fmt(format_args!("{}", icotable))?;

    // Make PQR file illustrating the electric potential at each vertex
    let mut pqr_file = File::create("potential.pqr")?;
    for (vertex_pos, data) in std::iter::zip(icotable.iter_positions(), icotable.vertex_data()) {
        pqr_write_atom(&mut pqr_file, 1, &vertex_pos.scale(*radius), *data, 2.0)?;
    }

    // Compare interpolated and exact potential linearly in angular space
    let mut pot_angles_file = File::create("pot_at_angles.dat")?;
    let mut pqr_file = File::create("potential_angles.pqr")?;
    writeln!(pot_angles_file, "# theta phi interpolated exact relerr")?;
    for theta in arange(0.0001..PI, resolution) {
        for phi in arange(0.0001..2.0 * PI, resolution) {
            let point: Vector3 = SphericalCoord::new(1.0, theta, phi).into();
            let interpolated = icotable.interpolate(&point);
            let exact = energy::electric_potential(&structure, &point.scale(*radius), &multipole);
            pqr_write_atom(&mut pqr_file, 1, &point.scale(*radius), exact, 2.0)?;
            let rel_err = (interpolated - exact) / exact;
            let abs_err = (interpolated - exact).abs();
            if abs_err > 0.05 {
                log::debug!(
                    "Potential at theta={:.3} phi={:.3} is {:.4} (exact: {:.4}) abs. error {:.4}",
                    theta,
                    phi,
                    interpolated,
                    exact,
                    abs_err
                );
                let face = icotable.nearest_face(&point);
                let bary = icotable.naive_barycentric(&point, &face);
                log::debug!("Face: {:?} Barycentric: {:?}\n", face, bary);
            }
            writeln!(
                pot_angles_file,
                "{:.3} {:.3} {:.4} {:.4} {:.4}",
                theta, phi, interpolated, exact, rel_err
            )?;
        }
    }
    Ok(())
}

// Wrapper for main function to handle errors
fn do_main() -> Result<()> {
    if std::env::var("RUST_LOG").is_err() {
        std::env::set_var("RUST_LOG", "info");
    }
    pretty_env_logger::init();

    let cli = Cli::parse();
    match cli.command {
        Some(cmd) => match cmd {
            Commands::Dipole { .. } => do_dipole(&cmd)?,
            Commands::Scan { .. } => do_scan(&cmd)?,
            Commands::Potential { .. } => do_potential(&cmd)?,
        },
        None => {
            bail!("No command given");
        }
    };
    Ok(())
}

fn main() -> ExitCode {
    if let Err(err) = do_main() {
        eprintln!("Error: {}", &err);
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    }
}
