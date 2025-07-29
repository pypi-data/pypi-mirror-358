//@HEADER
// ************************************************************************
//     Genten: Software for Generalized Tensor Decompositions
//     by Sandia National Laboratories
//
// Sandia National Laboratories is a multimission laboratory managed
// and operated by National Technology and Engineering Solutions of Sandia,
// LLC, a wholly owned subsidiary of Honeywell International, Inc., for the
// U.S. Department of Energy's National Nuclear Security Administration under
// contract DE-NA0003525.
//
// Copyright 2017 National Technology & Engineering Solutions of Sandia, LLC
// (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
// 1. Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
// ************************************************************************
//@HEADER

#pragma once

#include <cctype>

// Use constrained versions of some loss function
#define USE_CONSTRAINED_LOSS_FUNCTIONS 1

#include "Genten_GCP_GaussianLossFunction.hpp"
#include "Genten_GCP_RayleighLossFunction.hpp"
#include "Genten_GCP_GammaLossFunction.hpp"
#include "Genten_GCP_BernoulliLossFunction.hpp"
#include "Genten_GCP_PoissonLossFunction.hpp"


namespace Genten {

  template <typename Func>
  void dispatch_loss(const AlgParams& algParams, const Func& f)
  {
    // convert to lower-case
    std::string loss = algParams.loss_function_type;
    std::transform(loss.begin(), loss.end(), loss.begin(),
                   [](unsigned char c){return std::tolower(c);});

    if (loss == "gaussian")
      f(GaussianLossFunction(algParams));
    else if (loss == "rayleigh")
      f(RayleighLossFunction(algParams));
    else if (loss == "gamma")
      f(GammaLossFunction(algParams));
    else if (loss == "bernoulli")
      f(BernoulliLossFunction(algParams));
    else if (loss == "poisson")
      f(PoissonLossFunction(algParams));

    else
       Genten::error("Unknown loss function:  " + loss);
  }

  template <typename Func>
  void dispatch_loss(const AlgParams& algParams, Func& f)
  {
    // convert to lower-case
    std::string loss = algParams.loss_function_type;
    std::transform(loss.begin(), loss.end(), loss.begin(),
                   [](unsigned char c){return std::tolower(c);});

    if (loss == "gaussian")
      f(GaussianLossFunction(algParams));
    else if (loss == "rayleigh")
      f(RayleighLossFunction(algParams));
    else if (loss == "gamma")
      f(GammaLossFunction(algParams));
    else if (loss == "bernoulli")
      f(BernoulliLossFunction(algParams));
    else if (loss == "poisson")
      f(PoissonLossFunction(algParams));

    else
       Genten::error("Unknown loss function:  " + loss);
  }

}

#define GENTEN_INST_LOSS(SPACE,LOSS_INST_MACRO) \
  LOSS_INST_MACRO(SPACE,Genten::GaussianLossFunction) \
  LOSS_INST_MACRO(SPACE,Genten::RayleighLossFunction) \
  LOSS_INST_MACRO(SPACE,Genten::GammaLossFunction) \
  LOSS_INST_MACRO(SPACE,Genten::BernoulliLossFunction) \
  LOSS_INST_MACRO(SPACE,Genten::PoissonLossFunction) \

