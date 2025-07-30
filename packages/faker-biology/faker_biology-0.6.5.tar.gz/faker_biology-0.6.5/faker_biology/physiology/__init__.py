#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 10:20:19 2022

@author: richard
"""
from typing import Sequence
from faker.providers import BaseProvider
from faker_biology import BioProvider

from faker_biology.physiology.celltype_data import cell_types
from faker_biology.physiology.organs_data import organ_data
import faker_biology.physiology.organelles as organelle_data

class Organelle(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator)
        
    def _all(self):
        maj = [x for x in organelle_data.eukaryote_organelles['eukaryotes_major']]
        minor = [x  for x in organelle_data.eukaryote_organelles['eukaryotes_minor']]
        maj.extend(minor)
        return maj
    
    
    def _filtered(self, terms):
        orgs = self._all()
        filtered = [x['name'] for x in  filter(lambda x:x['distribution'] in terms, orgs )]
        return filtered
        
    def common_eukaryotic_organelle(self) -> str:
        """
        Gets an organelle name that appears in 'most' or 'all' organisms

        Returns
        -------
        A string

        """
        common = ['all', 'most']
        filtered = self._filtered(common)
        return self.random_element(filtered)
    
    def plant_organelle(self) -> str:
        """
        Gets an organelle present in plant cells
        Returns
        -------
        str
        """
        terms = ['all','most', 'plants']
        filtered = self._filtered(terms)
        return self.random_element(filtered)
    
    def animal_organelle(self) -> str:
        """
        Gets an organelle present in animal cells
        Returns
        -------
        str
        """
        terms = ['all', 'most', 'animals']
        filtered = self._filtered(terms)
        return self.random_element(filtered)
        
    def organelle(self) -> str:
        """
        A randomly selected cell organelle. Source Wikipedia 
        https://en.wikipedia.org/wiki/Organelle
        Returns
        -------
        str
            An organelle, e.g. 'nucleus'.

        """
        orgs = [x['name'] for x in self._all()]
        return self.random_element(orgs)

    

class CellType(BioProvider):
    """
     Provider of human cell type names. Source of data is Wikipedia:
         https://en.wikipedia.org/wiki/List_of_distinct_cell_types_in_the_adult_human_body
             
    """

    def __init__(self, generator):
        super().__init__(generator)

    def categories(self) -> Sequence[str]:
        """
        A list of cell-type categories
        """
        return list(cell_types.keys())

    def celltype(self) -> str:
        """
        Gets a random human cell type
        """
        leaves = []
        self._dict_leaves(cell_types, leaves)
        return self.random_element(leaves)


class Organ(BioProvider):
    """
     Provider of human organ names. Source of data is Wikipedia:
         https://en.wikipedia.org/wiki/List_of_organs_of_the_human_body
             
    """

    def __init__(self, generator):
        super().__init__(generator)

    def categories(self) -> Sequence[str]:
        """
        A list of organ categories
        """
        return list(organ_data.keys())

    def organ(self) -> str:
        """
        Gets a random mammalian organ
        """
        leaves = []
        self._dict_leaves(organ_data, leaves)
        return self.random_element(leaves)

    def non_reproductive_organ(self) -> str:
        """
        Gets a random non-reproductive organ
        """
        return self.random_element(self._generate_non_repr_organs())

    def _generate_non_repr_organs(self):
        if not hasattr(self, "_nonr_items"):
            categories = filter(lambda c: "eproductive" not in c, self.categories())
            self._nonr_items = []
            for c in categories:
                leaves_by_c = self._leaves_by_category(organ_data, c)
                # print (f" leaves by c = {leaves_by_c}")
                self._nonr_items.extend(leaves_by_c)
        return self._nonr_items
