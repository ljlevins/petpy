# encoding=utf-8

r"""

The :code:`api.py` file stores all the :code:`Petfinder` class and all associated functions and methods for
interacting with the Petfinder API. Before getting started with :code:`petpy`, please be sure to obtain an
API and secret key from Petfinder by registering for an account on the Petfinder developers page at
https://www.petfinder.com/developers/

"""

from pandas import DataFrame
from pandas.io.json import json_normalize
import requests
from urllib.parse import urljoin


class Petfinder(object):
    r"""
    Wrapper class for the PetFinder API.

    Attributes
    ----------
    host : str
        The base URL of the Petfinder API.
    key : str
        The key from the Petfinder API passed when the :code:`Petfinder` class is initialized.
    secret : str
        The secret key obtained from the Petfinder API passed when the :code:`Petfinder` class is initialized.
    auth : str
        The authorization token string returned when the connection to the Petfinder API is made with the specified
        :code:`key` and :code:`secret`.

    Methods
    -------
    animal_types(types, return_df=False)
        Returns data on an animal type, or types, available from the Petfinder API.
    breeds(types=None, return_df=False, raw_results=False)
        Returns available breeds of specified animal type(s) from the Petfinder API.
    animals(animal_id=None, animal_type=None, breed=None, size=None, gender=None, age=None, color=None,
            coat=None, status=None, name=None, organization_id=None, location=None, distance=None,
            sort=None, pages=None, results_per_page=20, return_df=False)
        Finds adoptable animals based on given criteria.
    organizations(organization_id=None, name=None, location=None, distance=None, state=None, country=None,
                  query=None, sort=None, results_per_page=20, pages=None, return_df=False)
        Finds animal organizations based on specified criteria in the Petfinder API database.

    """
    def __init__(self, key, secret):
        r"""
        Initialization method of the :code:`Petfinder` class.

        Parameters
        ----------
        key : str
            API key given after `registering on the PetFinder site <https://www.petfinder.com/developers/api-key>`_
        secret : str
            Secret API key given in addition to general API key. The secret key is required as of V2 of
            the PetFinder API and is obtained from the Petfinder website at the same time as the access key.

        """
        self.key = key
        self.secret = secret
        self.host = 'http://api.petfinder.com/v2/'
        self.auth = self._authenticate()

    def _authenticate(self):
        r"""
        Internal function for authenticating users to the Petfinder API.

        Raises
        ------

        Returns
        -------
        str
            Access token granted by the Petfinder API. The access token stays live for 3600 seconds, or one hour,
            at which point the user must reauthenticate.

        """
        endpoint = 'oauth2/token'

        url = urljoin(self.host, endpoint)

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.key,
            'client_secret': self.secret
        }

        r = requests.post(url, data=data)

        if r.json()['token_type'] == 'Bearer':
            return r.json()['access_token']

    def animal_types(self, types=None):
        r"""
        Returns data on an animal type, or types available from the Petfinder API. This data includes the
        available type's coat names and colors, gender and other specific information relevant to the
        specified type(s). The animal type must be of 'dog', 'cat', 'rabbit', 'small-furry', 'horse', 'bird',
        'scales-fins-other', 'barnyard'.

        Parameters
        ----------
        types : str, list or tuple, optional
            Specifies the animal type or types to return. Can be a string representing a single animal type, or a
            tuple or list of animal types if more than one type is desired. If not specified, all animal types are
            returned.

        Raises
        ------
        ValueError
            Raised when the :code:`types` parameter receives an invalid animal type.
        TypeError
            If the :code:`types` is not given either a str, list or tuple, or None, a :code:`TypeError` will be
            raised.

        Returns
        -------
        dict
            Dictionary object representing JSON data returned from the Petfinder API.

        """
        if types is not None:
            type_check = types
            if isinstance(types, str):
                type_check = [types]
            diff = set(type_check).difference(('dog', 'cat', 'rabbit', 'small-furry', 'horse', 'bird',
                                               'scales-fins-other', 'barnyard'))
            if len(diff) > 0:
                raise ValueError("animal types must be of the following 'dog', 'cat', 'rabbit', "
                                 "'small-furry', 'horse', 'bird', 'scales-fins-other', 'barnyard'")

        if types is None:
            url = urljoin(self.host, 'types')

            r = requests.get(url, headers={
                'Authorization': 'Bearer ' + self.auth,
            })

            result = r.json()

        elif isinstance(types, str):
            url = urljoin(self.host, 'types/{type}'.format(type=types))

            r = requests.get(url,
                             headers={
                                 'Authorization': 'Bearer ' + self.auth
                             })

            result = r.json()

        elif isinstance(types, (tuple, list)):
            types_collection = []

            for type in types:
                url = urljoin(self.host, 'types/{type}'.format(type=type))

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 })

                types_collection.append(r.json()['type'])

            result = {'type': types_collection}

        else:
            raise TypeError('types parameter must be either None, str, list or tuple')

        return result

    def breeds(self, types=None, return_df=False, raw_results=False):
        r"""
        Returns breed names of specified animal type, or types.

        Parameters
        ----------
        types :  str, list or tuple, optional
            String representing a single animal type or a list or tuple of a collection of animal types. If not
            specified, all available breeds for each animal type is returned. The animal type must be of 'dog',
            'cat', 'rabbit', 'small-furry', 'horse', 'bird', 'scales-fins-other', 'barnyard'.
        return_df : boolean, default False
            If :code:`True`, the result set will be coerced into a pandas :code:`DataFrame` with two columns,
            breed and name. If :code:`return_df` is set to :code:`True`, it will override the :code:`raw_result`
            parameter if it is also set to :code:`True` and return a pandas :code:`DataFrame`.
        raw_results: boolean, default False
            The PetFinder API :code:`breeds` endpoint returns some extraneous data in its result set along with the
            breed names of the specified animal type(s). If :code:`raw_results` is :code:`False`, the method will
            return a cleaner JSON object result set with the extraneous data removed. This parameter can be set to
            :code:`True` for those interested in retrieving the entire result set. If the parameter :code:`return_df`
            is set to :code:`True`, a pandas :code:`DataFrame` will be returned regardless of the value specified for
            the :code:`raw_result` parameter.

        Raises
        ------
        ValueError
            Raised when the :code:`types` parameter receives an invalid animal type.
        TypeError
            If the :code:`types` is not given either a str, list or tuple, or None, a :code:`TypeError` will be
            raised.

        Returns
        -------
        dict or pandas DataFrame
            If the parameter :code:`return_df` is :code:`False`, a dictionary object representing the JSON data
            returned from the Petfinder API is returned. If :code:`return_df=True`, the resulting dictionary is
            coerced into a pandas DataFrame. Note if :code:`return_df=True`, the parameter :code:`raw_results` is
            overridden.

        """
        if types is not None:
            type_check = types
            if isinstance(types, str):
                type_check = [types]
            diff = set(type_check).difference(('dog', 'cat', 'rabbit', 'small-furry', 'horse', 'bird',
                                               'scales-fins-other', 'barnyard'))
            if len(diff) > 0:
                raise ValueError("animal types must be of the following 'dog', 'cat', 'rabbit', "
                                 "'small-furry', 'horse', 'bird', 'scales-fins-other', 'barnyard'")

        if types is None or isinstance(types, (list, tuple)):
            breeds = []

            if types is None:
                types = ('dog', 'cat', 'rabbit', 'small-furry',
                         'horse', 'bird', 'scales-fins-other', 'barnyard')

            for t in types:
                url = urljoin(self.host, 'types/{type}/breeds'.format(type=t))

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 })

                breeds.append({t: r.json()})

            result = {'breeds': breeds}

        elif isinstance(types, str):
            url = urljoin(self.host, 'types/{type}/breeds'.format(type=types))

            r = requests.get(url,
                             headers={
                                 'Authorization': 'Bearer ' + self.auth
                             })

            result = r.json()

        else:
            raise TypeError('types parameter must be either None, str, list or tuple')

        if return_df:
            raw_results = True

            df_results = DataFrame()

            if isinstance(types, (tuple, list)):

                for t in range(0, len(types)):
                    df_results = df_results.append(json_normalize(result['breeds'][t][types[t]]['breeds']))

            else:
                df_results = df_results.append(json_normalize(result['breeds']))

            df_results.rename(columns={'_links.type.href': 'breed'}, inplace=True)
            df_results['breed'] = df_results['breed'].str.replace('/v2/types/', '').str.capitalize()

            result = df_results

        if not raw_results:

            json_result = {
                'breeds': {

                }
            }

            if isinstance(types, (tuple, list)):
                for t in range(0, len(types)):
                    json_result['breeds'][types[t]] = []

                    for breed in result['breeds'][t][types[t]]['breeds']:
                        json_result['breeds'][types[t]].append(breed['name'])

            else:
                json_result['breeds'][types] = []

                for breed in result['breeds']:
                    json_result['breeds'][types].append(breed['name'])

            result = json_result

        return result

    def animals(self, animal_id=None, animal_type=None, breed=None, size=None, gender=None,
                age=None, color=None, coat=None, status=None, name=None, organization_id=None,
                location=None, distance=None, sort=None, pages=None, results_per_page=20, return_df=False):
        r"""
        Returns adoptable animal data from Petfinder based on specified criteria.

        Parameters
        ----------
        animal_id : int, tuple or list of int, optional
        animal_type : optional
        breed: optional
        size: optional
        gender : optional
        age : optional
        color : optional
        coat : optional
        status : optional
        name : optional
        organization_id : optional
        location : optional
        distance : optional
        sort : optional
        pages : int, default None
        results_per_page : int, default 20
        return_df : boolean, default False

        Raises
        ------
        TypeError

        Returns
        -------
        dict or pandas DataFrame

        """
        max_page_warning = False

        if animal_id is not None:

            url = urljoin(self.host, 'animals/{id}')

            if isinstance(animal_id, (tuple, list)):

                animals = []

                for ani_id in animal_id:
                    r = requests.get(url.format(id=ani_id),
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     })

                    animals.append(r.json()['animal'])

            else:
                r = requests.get(url.format(id=animal_id),
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 })

                animals = r.json()['animal']

        else:

            url = urljoin(self.host, 'animals/')

            params = _parameters(animal_type=animal_type, breed=breed, size=size, gender=gender,
                                 age=age, color=color, coat=coat, status=status, name=name,
                                 organization_id=organization_id, location=location, distance=distance,
                                 sort=sort, results_per_page=results_per_page)

            if pages is None:
                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 },
                                 params=params)

                animals = r.json()['animals']

            else:
                pages += 1
                params['page'] = 1

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 },
                                 params=params)

                animals = r.json()['animals']

                max_pages = r.json()['pagination']['total_pages']

                if pages > int(max_pages):
                    pages = max_pages
                    max_page_warning = True

                for page in range(2, pages):

                    params['page'] = page

                    r = requests.get(url,
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     },
                                     params=params)

                    for i in r.json()['animals']:
                        animals.append(i)

        animals = {
            'animals': animals
        }

        if return_df:
            animals = json_normalize(animals['animals'])

        if max_page_warning:
            print('pages parameter exceeded maximum number of available pages available from the Petfinder API. As '
                  'a result, the maximum number of pages {max_page} was returned'.format(max_page=max_pages))

        return animals

    def organizations(self, organization_id=None, name=None, location=None, distance=None, state=None,
                      country=None, query=None, sort=None, results_per_page=20, pages=None, return_df=False):
        r"""

        Parameters
        ----------
        organization_id : optional
        name : optional
        location : optional
        distance : optional
        state : optional
        country : optional
        query : optional
        sort : optional
        pages : int, default None
        results_per_page : int, default 20
        return_df : boolean, default False

        Raises
        ------
        TypeError


        Returns
        -------
        dict or pandas DataFrame

        """
        max_page_warning = False

        if organization_id is not None:

            url = urljoin(self.host, 'organizations/{id}')

            if isinstance(organization_id, (tuple, list)):

                organizations = []

                for org_id in organization_id:
                    r = requests.get(url.format(id=org_id),
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     })

                    organizations.append(r.json()['organization'])

            else:
                r = requests.get(url.format(id=organization_id),
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 })

                organizations = r.json()['organization']

        else:

            url = urljoin(self.host, 'organizations/')

            params = _parameters(name=name, location=location, distance=distance,
                                 state=state, country=country, query=query, sort=sort,
                                 results_per_page=results_per_page)

            if pages is None:

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 },
                                 params=params)
                
                organizations = r.json()['organizations']
                
            else:
                pages += 1
                params['page'] = 1

                r = requests.get(url,
                                 headers={
                                     'Authorization': 'Bearer ' + self.auth
                                 },
                                 params=params)

                organizations = r.json()['organizations']

                max_pages = r.json()['pagination']['total_pages']

                if pages > int(max_pages):
                    pages = max_pages
                    max_page_warning = True

                for page in range(2, pages):

                    params['page'] = page

                    r = requests.get(url,
                                     headers={
                                         'Authorization': 'Bearer ' + self.auth
                                     },
                                     params=params)

                    for i in r.json()['organizations']:
                        organizations.append(i)

        organizations = {
            'organizations': organizations
        }

        if return_df:
            organizations = json_normalize(organizations['organizations'])

        if max_page_warning:
            print('pages parameter exceeded maximum number of available pages available from the Petfinder API. As '
                  'a result, the maximum number of pages {max_page} was returned'.format(max_page=max_pages))

        return organizations


def _parameters(animal=None, breed=None, size=None, gender=None, color=None, coat=None, animal_type=None,
                location=None, distance=None, state=None, country=None, query=None, sort=None, name=None,
                age=None, animal_id=None, organization_id=None, status=None, results_per_page=None, page=None):
    r"""
    Internal function for determining which parameters have been passed and aligning them to their respective
    Petfinder API parameters.

    Parameters
    ----------
    animal :
    :param breed:
    :param size:
    :param gender:
    :param color:
    :param coat:
    :param animal_type:
    :param location:
    :param distance:
    :param state:
    :param country:
    :param query:
    :param sort:
    :param name:
    :param age:
    :param animal_id:
    :param organization_id:
    :param status:
    :param results_per_page:
    :param page:

    Returns
    -------


    """
    _check_parameters(animal_types=animal_type, size=size, gender=gender, age=age, coat=coat, status=status,
                      location=location, distance=distance, sort=sort, limit=results_per_page)

    args = {
        'animal': animal,
        'breed': breed,
        'size': size,
        'gender': gender,
        'age': age,
        'color': color,
        'coat': coat,
        'animal_type': animal_type,
        'location': location,
        'distance': distance,
        'state': state,
        'country': country,
        'query': query,
        'sort': sort,
        'name': name,
        'animal_id': animal_id,
        'organization_id': organization_id,
        'status': status,
        'limit': results_per_page,
        'page': page
    }

    args = {key: val for key, val in args.items() if val is not None}

    return args


def _check_parameters(animal_types=None, size=None, gender=None, age=None, coat=None, status=None,
                      location=None, distance=None, sort=None, limit=None):
    r"""
    Internal function for checking the passed parameters against valid options available in the Petfinder API.

    Parameters
    ----------
    animal_types :
    :param size:
    :param gender:
    :param age:
    :param coat:
    :param status:
    :param location:
    :param distance:
    :param sort:
    :param limit:

    Raises
    ------
    ValueError

    Returns
    -------
    None
        If :code:`ValueError` is not raised, the function returns :code:`None` which signifies the passed API
        parameters are valid.

    """
    _animal_types = ('dog', 'cat', 'rabbit', 'small-furry',
                     'horse', 'bird', 'scales-fins-other', 'barnyard')
    _sizes = ('small', 'medium', 'large', 'xlarge')
    _genders = ('male', 'female', 'unknown')
    _ages = ('baby', 'young', 'adult', 'senior')
    _coats = ('short', 'medium', 'long', 'wire', 'hairless', 'curly')
    _status = ('adoptable', 'adopted', 'found')
    _location = ('city,state', 'latitude,longitude', 'postal code')
    _sort = ('recent', '-recent', 'distance', '-distance')

    incorrect_values = {}

    if animal_types is not None and animal_types not in _animal_types:
        incorrect_values['animal_types'] = "animal types {types} is not valid. Animal types " \
                                           "must of the following: {animal_types}"\
            .format(types=animal_types,
                    animal_types=_animal_types)

    if size is not None:
        if isinstance(size, str):
            size = [size]
        diff = set(size).difference(_sizes)

        if len(diff) > 0:
            incorrect_values['size'] = "sizes {sizes} are not valid. Sizes must be of the following: {size_list}"\
                .format(sizes=diff,
                        size_list=_sizes)

    if gender is not None:
        if isinstance(gender, str):
            gender = [gender]
        diff = set(gender).difference(_genders)

        if len(diff) > 0:
            incorrect_values['gender'] = "genders {genders} are not valid. Genders must be of the following: " \
                                         "{gender_list}"\
                .format(genders=diff,
                        gender_list=_genders)

    if age is not None:
        if isinstance(age, str):
            age = [age]
        diff = set(age).difference(_ages)

        if len(diff) > 0:
            incorrect_values['age'] = "ages {age} are not valid. Ages must be of the following: " \
                                      "{ages_list}"\
                .format(age=diff,
                        ages_list=_ages)

    if coat is not None:
        if isinstance(coat, str):
            coat = [coat]
        diff = set(coat).difference(_coats)

        if len(diff) > 0:
            incorrect_values['coat'] = "coats {coats} are not valid. Coats must be of the following: " \
                                       "{coat_list}"\
                .format(coats=diff,
                        coat_list=_coats)

    if status is not None and status not in _status:
        incorrect_values['status'] = "animal status {status} is not valid. Status must be of the following: " \
                                     "{statuses}".format(status=status,
                                                         statuses=_status)

    if sort is not None and sort not in _sort:
        incorrect_values['sort'] = "sort order {sort} must be one of: {sort_list}"\
            .format(sort=sort,
                    sort_list=_sort)

    if location is not None and location not in _location:
        incorrect_values['location'] = "location {location} must be one of: {locations}"\
            .format(location=location,
                    locations=_location)

    if distance is not None:
        if int(distance) > 500:
            incorrect_values['distance'] = "distance cannot be greater than 500"

    if limit is not None:
        if int(limit) > 100:
            incorrect_values['limit'] = "results per page cannot be greater than 100"

    if len(incorrect_values) > 0:
        errors = ''
        for k, v in incorrect_values.items():
            errors = errors + v + '\n'

        raise ValueError(errors)

    return None


def _coerce_to_dataframe(results):
    r"""
    Internal function for coercing results from the Petfinder API into a pandas DataFrame.

    Parameters
    ----------
    results:

    Returns
    -------
    pandas DataFrame
        pandas DataFrame coerced from resulting JSON data returned from the Petfinder API

    """
    key = list(results.keys())[0]
    results_df = json_normalize(results[key])

    if key == 'animals':
        results_df.rename(columns={'_links.organizations.href': 'organization_id',
                                   '_links.self.href': 'animal_id',
                                   '_links.type.href': 'animal_type'}, inplace=True)

        results_df['organization_id'] = results_df['organization_id'].str.replace('/v2/organizations/', '')
        results_df['animal_id'] = results_df['animal_id'].str.replace('/v2/animals/', '')
        results_df['animal_type'] = results_df['animal_type'].str.replace('/v2/types/', '')

    if key == 'organizations':
        del results_df['_links.animals.href']

        results_df.rename(columns={'_links.self.href': 'organization_id'}, inplace=True)

        results_df['organization_id'] = results_df['organization_id'].str.replace('/v2/organizations/', '')

    return results_df
