import src.home.util_similarity as util_similarity


def array_equals(array1, array2):
    # Verificar se ambos os arrays têm o mesmo tamanho
    if len(array1) != len(array2):
        return False

    # Verificar se todos os elementos em ambos os arrays são iguais
    return all(elemento1 == elemento2 for elemento1, elemento2 in zip(array1, array2))


class TestUtilSimilarity:
    def test_lin_similarity(self):
        assert util_similarity.lin_similarity('car','car') == 1.0
        assert util_similarity.lin_similarity('car','truck') == 0.8994141506517801

    def test_split_compound_name_1(self):
        result = util_similarity.split_compound_name('CollegeLibraryApplication')
        assert len(result) == 3
        assert util_similarity.print_compound_name_array(result) == util_similarity.print_compound_name_array(['College','Library','Application'])

    def test_split_compound_name_2(self):
        result = util_similarity.split_compound_name('T_TTApplicationCNISDatabaseTestTTTXXX_Azul')
        assert 8 == len(result)
        assert array_equals(['T','TT','Application','CNIS','Database','Test','TTTXXX','Azul'],result)
    
    def test_split_compound_name_3(self):
        result = util_similarity.split_compound_name('_SensorID')
        assert 2 == len(result)
        assert array_equals(['Sensor','ID'],result)
    
    def test_split_compound_name_4(self):
        result = util_similarity.split_compound_name('sensorID')
        assert 2 == len(result)
        assert array_equals(['sensor','ID'],result)

    def test_compound_lin_similarity_1(self):
        result = util_similarity.compound_lin_similarity('CollegeLibraryApplication','CollegeLibraryApplication')
        assert 1.0 == result

    def test_compound_lin_similarity_2(self):
        result = util_similarity.compound_lin_similarity('CollegeLibraryApplication','SchoolLibraryApplication')
        assert 0.804372372865161 == result

    def test_compound_lin_similarity_3(self):
        result = util_similarity.compound_lin_similarity('Application', 'SchoolLibraryApplication')
        assert 0.3333333333333333 == result
        result = util_similarity.compound_lin_similarity('SchoolLibraryApplication', 'Application')
        assert 0.3333333333333333 == result


